#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Logging in nomad is structured. Structured logging means that log entries contain
dictionaries with quantities related to respective events. E.g. having the code,
parser, parser version, entry_id, mainfile, etc. for all events that happen during
entry processing. This means the `get_logger` and all logger functions
take keyword arguments for structured data. Otherwise `get_logger` can
be used similar to the standard `logging.getLogger`.
"""

import json
import logging
import os.path
import re
from logging.handlers import WatchedFileHandler
from typing import Any, cast

import logstash
import structlog
from structlog.processors import (
    JSONRenderer,
    StackInfoRenderer,
    TimeStamper,
    format_exc_info,
)
from structlog.stdlib import LoggerFactory

from nomad import utils
from nomad.config import config


def sanitize_logevent(event: str) -> str:
    """
    Prepares a log event or message for analysis in elastic stack. It removes numbers,
    list, and matrices of numbers from the event string and limits its size. The
    goal is to make it easier to define aggregations over events by using event
    strings as representatives for event classes rather than event instances (with
    concrete numbers, etc).
    """
    sanitized_event = event[:120]
    sanitized_event = re.sub(r'(\d*\.\d+|\d+(\.\d*)?)', 'X', sanitized_event)
    sanitized_event = re.sub(
        r'((\[|\()\s*)?X\s*(,\s*X)+(\s*(\]|\)))?', 'L', sanitized_event
    )
    sanitized_event = re.sub(
        r'((\[|\()\s*)?[XL](,\s*[XL])+(\s*(\]|\)))?', 'M', sanitized_event
    )
    return sanitized_event


class BaseHandler(logging.Handler):
    """A Handler base class that filters logs for being structlog entries."""

    def filter(self, record):
        if record.name.startswith('nomad.logtransfer'):
            # We filter out all logtransfer logs, as they might cause
            # infinite loops with only logtransfer errors and not transffered
            # logs.
            return False

        if record.name == 'uvicorn.access':
            http_access_path = record.args[2]
            if 'alive' in http_access_path or 'gui/index.html' in http_access_path:
                return False

        if super().filter(record):
            is_structlog = False
            if isinstance(record.msg, str):
                is_structlog = record.msg.startswith('{') and record.msg.endswith('}')

            if is_structlog:
                return True

        return False


class LogstashHandler(logstash.TCPLogstashHandler, BaseHandler):
    """A log handler that emits records to logstash."""

    def __init__(self):
        super().__init__(config.logstash.host, config.logstash.tcp_port, version=1)


class LogstashFormatter(logstash.formatter.LogstashFormatterBase):
    def format(self, record):
        try:
            structlog = json.loads(record.getMessage())
        except json.JSONDecodeError:
            structlog = dict(event=record.getMessage())

        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@version': '1',
            'event': structlog.get('event', 'unknown event'),
            'host': self.host,
            'path': record.pathname,
            'tags': self.tags,
            'type': self.message_type,
            # Extra Fields
            'level': record.levelname,
            'logger_name': record.name,
            # Nomad specific
            'nomad.service': config.meta.service,
            'nomad.deployment': config.meta.deployment,
            'nomad.version': config.meta.version,
            'nomad.commit': '',
        }
        if config.meta.label:
            message['nomad.label'] = config.meta.label

        if record.name.startswith('nomad'):
            for key, value in structlog.items():
                if key in ('event', 'stack_info', 'id', 'timestamp'):
                    continue
                elif key == 'exception':
                    exception_trace = value.strip('\n')
                    message['digest'] = str(value)[-256:]
                    # exclude the last line, which is the exception message and might
                    # vary for different instances of the same exception
                    message['exception_hash'] = utils.hash(
                        exception_trace[: exception_trace.rfind('\n')]
                    )
                elif key in [
                    'upload_id',
                    'entry_id',
                    'dataset_id',
                    'user_id',
                    'mainfile',
                ]:
                    key = f'nomad.{key}'
                else:
                    key = f'{record.name}.{key}'

                message[key] = value
        else:
            message.update(structlog)

        # Handle uvicorn access events
        if record.name == 'uvicorn.access':
            status_code = getattr(record, 'status_code', None)
            if status_code is not None:
                message['uvicorn.status_code'] = status_code
            scope = getattr(record, 'scope', None)
            if scope is not None:
                message['uvicorn.method'] = scope['method']
                message['uvicorn.path'] = scope['path']
                message['uvicorn.query_string'] = scope['query_string'].decode()
                message['uvicorn.headers'] = {
                    key.decode(): value.decode() for key, value in scope['headers']
                }
            args = getattr(record, 'args', None)
            if args is not None and len(args) == 5:
                _, method, path_w_query, _, status_code = args
                path_w_query_components = path_w_query.split('?', 1)
                path = path_w_query_components[0]
                if len(path_w_query_components) == 2:
                    query_string = path_w_query_components[1]
                    message['uvicorn.query_string'] = query_string
                message['uvicorn.method'] = method
                message['uvicorn.path'] = path
                message['uvicorn.status_code'] = status_code
        else:
            # Add extra fields
            message.update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)


class LogtransferFormatter(LogstashFormatter):
    def serialize(self, message):
        return json.dumps(message)


class ConsoleFormatter(LogstashFormatter):
    def __init__(self, message_type='Logstash', tags=None, fqdn=False, datefmt=None):
        # In conftest.py, we monkeypatch the logging.Formatter with ConsoleFormatter.
        # Since pytest instantiates this formatter with the datefmt argument,
        # we need to add this init method to logstashformatter to ensure proper functioning with pytest.
        # LogstashFormatter does not accept the datefmt argument.
        super().__init__(message_type=message_type, tags=tags, fqdn=fqdn)

    short_format = False

    @classmethod
    def serialize(cls, message_dict):
        from io import StringIO

        logger = message_dict.pop('logger_name', 'unknown logger')
        event = message_dict.pop('event', None)
        level = message_dict.pop('level', 'UNKNOWN')
        exception = message_dict.pop('exception', None)
        time = message_dict.pop('@timestamp', '1970-01-01 12:00:00')

        for key in [
            'type',
            'tags',
            'stack_info',
            'path',
            'message',
            'host',
            '@version',
            'digest',
        ]:
            message_dict.pop(key, None)
        keys = list(message_dict.keys())
        keys.sort()

        out = StringIO()
        out.write(
            f'{level.ljust(8)} {logger.ljust(20)[:20]} {time.ljust(19)[:19]} {event}'
        )
        if exception is not None:
            out.write(
                '\n  - exception: {}'.format(str(exception).replace('\n', '\n    '))
            )

        for key in keys:
            if cls.short_format and key.startswith('nomad.'):
                print_key = key[6:]
            else:
                print_key = key
            if not cls.short_format or print_key not in ['deployment', 'service']:
                out.write(f'\n  - {print_key}: {str(message_dict.get(key, None))}')
        return out.getvalue()


class LogtransferHandler(WatchedFileHandler):
    def __init__(self):
        super().__init__(os.path.join(config.fs.tmp, config.logtransfer.log_file))


def add_logstash_handler(logger):
    logstash_handler = next(
        (
            handler
            for handler in logger.handlers
            if isinstance(handler, LogstashHandler)
        ),
        None,
    )

    if logstash_handler is None:
        logstash_handler = LogstashHandler()
        logstash_handler.formatter = LogstashFormatter(
            tags=['nomad', config.meta.deployment]
        )
        logstash_handler.setLevel(config.logstash.level)
        logger.addHandler(logstash_handler)


root = logging.getLogger()


def get_logtransfer_handler(logger=root):
    logtransfer_handler = next(
        (
            handler
            for handler in logger.handlers
            if isinstance(handler, LogtransferHandler)
        ),
        None,
    )

    return logtransfer_handler


def add_logtransfer_handler(logger):
    logtransfer_handler = get_logtransfer_handler(logger)

    if logtransfer_handler is None:
        logtransfer_handler = LogtransferHandler()
        logtransfer_handler.formatter = LogtransferFormatter(
            tags=['nomad', config.meta.deployment]
        )
        logtransfer_handler.setLevel(config.logtransfer.level)
        logger.addHandler(logtransfer_handler)


def get_logger(name, **kwargs):
    """
    Returns a structlog logger that is already attached with a logstash handler.
    Use additional *kwargs* to pre-bind some values to all events.
    """
    if name.startswith('nomad.'):
        name = '.'.join(name.split('.')[:2])

    logger = structlog.get_logger(name, **kwargs)
    return logger


# configure structlog
log_processors = [
    StackInfoRenderer(),
    format_exc_info,
    TimeStamper(fmt='%Y-%m-%d %H:%M.%S', utc=False),
    JSONRenderer(sort_keys=True),
]

default_factory = LoggerFactory()


def logger_factory(*args):
    logger = default_factory(*args)
    logger.setLevel(logging.DEBUG)
    return logger


structlog.configure(
    processors=cast(Any, log_processors),
    logger_factory=logger_factory,
    wrapper_class=structlog.stdlib.BoundLogger,
)


# configure logging in general
def configure_logging(console_log_level=config.services.console_log_level):
    logging.basicConfig(level=logging.DEBUG)

    for handler in root.handlers:
        if not isinstance(
            handler,
            LogstashHandler | LogtransferHandler,
        ):
            handler.setLevel(console_log_level)
            handler.setFormatter(ConsoleFormatter())


configure_logging()


# configure logstash
if config.logstash.enabled:
    add_logstash_handler(root)

    get_logger(__name__).info(
        'setup logstash logging',
        logstash=config.logstash.enabled,
        logstash_host=config.logstash.host,
        logstash_port=config.logstash.tcp_port,
        logstash_level=config.logstash.level,
    )

if config.logtransfer.enabled:
    add_logtransfer_handler(root)
    get_logger(__name__).info(
        'setup logtransfer logging', logtransfer=config.logtransfer.enabled
    )

# configure log levels
for logger in ['elasticsearch', 'urllib3.connectionpool', 'celery']:
    logging.getLogger(logger).setLevel(logging.WARNING)
