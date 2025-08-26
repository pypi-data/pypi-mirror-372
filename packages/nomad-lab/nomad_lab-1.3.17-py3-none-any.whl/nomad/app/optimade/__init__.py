import os
import sys
import importlib
import warnings


warnings.filterwarnings('ignore', message=r'v0\.17 of the `optimade` package.*')


# patch optimade python tools config (patched module most be outside this module to force import before optimade)
os.environ['OPTIMADE_CONFIG_FILE'] = os.path.join(
    os.path.dirname(__file__), 'optimade_config.json'
)

# patch optimade logger (patched module most be outside this module to force import before optimade)
sys.modules['optimade.server.logger'] = importlib.import_module(
    'nomad.app.optimade_logger'
)

from pydantic import Field, create_model
from typing import Annotated


# optimade v1.0.6 and higher has a custom str pattern validator that fails for the `_nmd` prefix
# earlier versions fail pydantic validation for the default email field, so we will just patch the
# models to accept any string.

EntryInfoResource = create_model(
    'EntryInfoResource',
    formats=(
        Annotated[
            list[str],
            Field(
                description='List of output formats available for this type of entry.'
            ),
        ]
    ),
    description=(Annotated[str, Field(description='Description of the entry.')], ...),
    properties=(
        Annotated[
            dict[str, dict],
            Field(
                description='A dictionary describing queryable properties for this entry type.'
            ),
        ],
        ...,
    ),
    output_fields_by_format=(
        Annotated[
            dict[str, list[str]],
            Field(description='Dictionary of available output fields.'),
        ],
        ...,
    ),
)

EntryInfoResource = create_model(
    'EntryInfoResource',
    formats=(
        Annotated[
            list[str],
            Field(
                description='List of output formats available for this type of entry.'
            ),
        ]
    ),
    description=(Annotated[str, Field(description='Description of the entry.')], ...),
    properties=(
        Annotated[
            dict[str, dict],
            Field(
                description='A dictionary describing queryable properties for this entry type.'
            ),
        ],
        ...,
    ),
    output_fields_by_format=(
        Annotated[
            dict[str, list[str]],
            Field(description='Dictionary of available output fields.'),
        ],
        ...,
    ),
)
from optimade.models.optimade_json import Success


class EntryInfoResponse(Success):
    data: Annotated[  # type: ignore
        EntryInfoResource,  # type: ignore
        Field(description='OPTIMADE information for an entry endpoint.'),
    ]


for name, module in list(sys.modules.items()):
    if 'optimade' in name and hasattr(module, 'EntryInfoResource'):
        module.EntryInfoResource = EntryInfoResource  # type: ignore
    if 'optimade' in name and hasattr(module, 'ValidIdentifier'):
        module.ValidIdentifier = str  # type: ignore
    if 'optimade' in name and hasattr(module, 'EntryInfoResponse'):
        module.EntryInfoResponse = EntryInfoResponse  # type: ignore
# patch optimade base path
from nomad import utils  # nopep8
from nomad.config import config
from optimade.server.config import CONFIG  # nopep8

CONFIG.root_path = f'{config.services.api_base_path}/optimade'
CONFIG.base_url = '{}://{}'.format(
    'https' if config.services.https else 'http',
    config.services.api_host.strip('/'),
)


from .common import provider_specific_fields, create_provider_field  # nopep8


CONFIG.provider_fields = dict(
    structures=[
        create_provider_field(name, quantity.annotation.definition)
        for name, quantity in provider_specific_fields().items()
    ]
    + [
        dict(name='archive_url', description='', type='string', sortable=False),
        dict(name='entry_page_url', description='', type='string', sortable=False),
        dict(
            name='raw_file_download_url', description='', type='string', sortable=False
        ),
    ]
)


from optimade.server import main as optimade  # nopep8
from optimade.server.routers import structures  # nopep8

# remove all the test data
from optimade.server.routers import ENTRY_COLLECTIONS  # nopep8

for name, collection in ENTRY_COLLECTIONS.items():
    if name == 'links':
        collection.collection.drop()
        collection.collection.insert_one(
            {
                'id': 'index',
                'type': 'links',
                'name': 'Index meta-database',
                'description': 'Index for NOMAD databases',
                'base_url': 'http://providers.optimade.org/index-metadbs/nmd',
                'homepage': 'https://nomad-lab.eu',
                'link_type': 'root',
            }
        )
    else:
        collection.collection.drop()

# patch the structure collection with out elasticsearch implementation
from .elasticsearch import StructureCollection  # nopep8

# from optimade.server.entry_collections.elasticsearch import ElasticCollection
from .filterparser import parse_filter  # nopep8


structures.structures_coll = StructureCollection()
optimade.add_major_version_base_url(optimade.app)

# patch exception handlers
logger = utils.get_logger(__name__)
exception_handlers = sys.modules['optimade.server.exception_handlers']
original_handler = getattr(exception_handlers, 'general_exception')


def general_exception(request, exc, status_code=500, **kwargs):
    if getattr(exc, 'status_code', status_code) >= 500:
        logger.error(
            'unexpected exception in optimade implementation',
            status_code=status_code,
            exc_info=exc,
            url=request.url,
        )

    return original_handler(request, exc, status_code, **kwargs)


setattr(exception_handlers, 'general_exception', general_exception)


@optimade.app.on_event('startup')
async def startup_event():
    from optimade.server.warnings import OptimadeWarning
    import warnings

    warnings.filterwarnings('ignore', category=OptimadeWarning)


# "export" the app object
optimade_app = optimade.app
