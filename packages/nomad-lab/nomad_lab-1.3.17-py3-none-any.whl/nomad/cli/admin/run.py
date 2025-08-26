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

import click

from nomad import utils
from nomad.config import config

from .admin import admin


@admin.group(help='Run a nomad service locally (outside docker).')
def run():
    pass


@run.command(help='Run the jupyter hub.')
def hub():
    run_hub()


@run.command(help='Run the orchestrator internal worker.')
@click.option('--workers', type=int, default=12, help='Number of worker threads.')
def orchestrator_internal_worker(workers: int):
    run_temporal_worker(workers=workers)


@run.command(help='Run the nomad development worker.')
@click.option('--workers', type=int, default=None, help='Number of celery workers.')
def worker(**kwargs):
    run_worker(**kwargs)


@run.command(help='Run the nomad development app with all apis.')
@click.option(
    '--with-gui',
    help='The app will configure the gui for production and service it.',
    is_flag=True,
)
@click.option('--host', type=str, help='Passed as host parameter.')
@click.option('--port', type=int, help='Passed as port parameter.')
@click.option('--log-config', type=str, help='Passed as log-config parameter.')
@click.option(
    '--gunicorn',
    is_flag=True,
    type=bool,
    help='Run app with gunicorn instead of uvicorn.',
)
@click.option('--workers', type=int, help='Passed to uvicorn workers parameter.')
def app(with_gui: bool, **kwargs):
    run_app(with_gui=with_gui, **kwargs)


def run_temporal_worker(workers: int = 12):
    import asyncio

    from nomad.orchestrator.workers import internal_worker

    asyncio.run(internal_worker.run_worker(workers=workers))


def run_app(
    *,
    with_gui: bool = False,
    gunicorn: bool = False,
    host: str = None,
    log_config: str = None,
    port: int = None,
    **kwargs,
):
    config.meta.service = 'app'
    host = host or config.services.api_host or '0.0.0.0'
    # TODO: respect `config.services.api_port` instead of defaulting to 8000
    # port = int(port or config.services.api_port or 8000)
    port = int(port or 8000)

    if with_gui:
        import glob
        import os
        import os.path
        import shutil

        gui_folder = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../app/static/gui')
        )
        run_gui_folder = os.path.join(
            config.fs.working_directory, 'run', 'gui_configured'
        )
        if not os.path.exists(run_gui_folder):
            os.makedirs(run_gui_folder)

        # copy
        shutil.rmtree(run_gui_folder, ignore_errors=True)
        shutil.copytree(gui_folder, run_gui_folder)

        # replace base path in all GUI files
        source_file_globs = [
            '**/*.json',
            '**/*.html',
            '**/*.js',
            '**/*.js.map',
            '**/*.css',
        ]
        for source_file_glob in source_file_globs:
            source_files = glob.glob(
                os.path.join(run_gui_folder, source_file_glob), recursive=True
            )
            for source_file in source_files:
                with open(source_file) as f:
                    file_data = f.read()
                file_data = file_data.replace(
                    '/fairdi/nomad/latest', config.services.api_base_path
                )
                with open(source_file, 'w') as f:
                    f.write(file_data)

        # App and gui are served from the same server, same port. Replace the base urls with
        # relative paths
        config.ui.app_base = f'{config.services.api_base_path.rstrip("/")}'
        config.ui.north_base = f'{config.services.api_base_path.rstrip("/")}/north'

    from nomad.utils import get_logger

    if gunicorn:
        import logging.config

        from gunicorn.app.wsgiapp import WSGIApplication

        if log_config:
            logging.config.fileConfig(log_config)

        if not kwargs.get('workers', None):
            kwargs['workers'] = 4

        class App(WSGIApplication):
            def __init__(self):
                self.app_uri = 'nomad.app.main:app'
                super().__init__()

            def load_config(self):
                self.cfg.set('timeout', config.services.api_timeout)
                self.cfg.set('worker_class', 'uvicorn.workers.UvicornWorker')
                self.cfg.set('bind', f'{host}:{port}')
                for key, value in kwargs.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key, value)

        gunicorn_app = App()
        get_logger(__name__).info('created gunicorn server', data=str(gunicorn_app.cfg))
        gunicorn_app.run()
    else:
        from uvicorn import Config, Server

        kwargs['log_config'] = log_config

        uv_config = Config(
            'nomad.app.main:app',
            log_level='info',
            host=host,
            port=port,
            **{k: v for k, v in kwargs.items() if v is not None},
        )

        server = Server(config=uv_config)
        get_logger(__name__).info('created uvicorn server', data=uv_config.__dict__)
        server.run()


def run_worker(*, workers=None):
    config.meta.service = 'worker'
    from nomad import processing

    params = ['worker', '--loglevel=INFO', '-B', '-Q', 'celery']

    if workers is not None:
        params.append(f'--concurrency={workers}')

    processing.app.worker_main(params)


def run_hub():
    import os
    import subprocess
    import sys

    from jupyterhub.app import main

    if 'JUPYTERHUB_CRYPT_KEY' not in os.environ:
        crypt_key = config.north.jupyterhub_crypt_key
        if crypt_key is None:
            crypt_key = (
                subprocess.check_output('openssl rand -hex 32'.split(' '))
                .decode()
                .strip('\n')
            )
        os.environ['JUPYTERHUB_CRYPT_KEY'] = crypt_key

    config.meta.service = 'hub'
    sys.exit(
        main(argv=['-f', 'nomad/jupyterhub_config.py', '--Application.log_level=INFO'])
    )


def task_app(**kwargs):
    logger = utils.get_logger('app')
    try:
        run_app(**kwargs)
    except Exception as error:
        logger.exception(error)


def task_worker(**kwargs):
    logger = utils.get_logger('worker')
    try:
        run_worker(**kwargs)
    except Exception as error:
        logger.exception(error)


def run_appworker(
    *,
    app_host: str = None,
    app_port: int = None,
    fastapi_workers: int = None,
    celery_workers: int = None,
    dev: bool = False,
):
    from concurrent import futures as concurrent_futures

    if dev:
        fastapi_workers = 1
        celery_workers = 1

    with concurrent_futures.ProcessPoolExecutor(2) as executor:
        results = []

        def _submit(*args, **kwargs):
            results.append(executor.submit(*args, **kwargs))

        if config.temporal.enabled:
            _submit(run_temporal_worker, workers=celery_workers)
        else:
            _submit(task_worker, workers=celery_workers)
        _submit(task_app, workers=fastapi_workers, host=app_host, port=app_port)

        try:
            for future in concurrent_futures.as_completed(results):
                future.result()
        except KeyboardInterrupt:
            for future in results:
                future.cancel()
            executor.shutdown(wait=False)


@run.command(help='Run both app and worker.')
@click.option(
    '--app-host', type=str, default=None, help='Passed as app host parameter.'
)
@click.option(
    '--app-port', type=int, default=None, help='Passed as app port parameter.'
)
@click.option(
    '--fastapi-workers', type=int, default=None, help='Number of FastAPI workers.'
)
@click.option(
    '--celery-workers', type=int, default=None, help='Number of Celery workers.'
)
@click.option(
    '--dev', is_flag=True, default=False, help='Use one worker (for dev. env.).'
)
def appworker(**kwargs):
    run_appworker(**kwargs)
