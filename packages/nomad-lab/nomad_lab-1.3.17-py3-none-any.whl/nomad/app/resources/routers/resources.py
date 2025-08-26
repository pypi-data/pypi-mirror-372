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

import asyncio
import io
import os
import re
from datetime import datetime
from enum import Enum
from typing import Any

import ase.io
import bs4
import httpx
from anyio.from_thread import start_blocking_portal
from fastapi import APIRouter
from fastapi import Query as FastApiQuery
from mongoengine import (
    BooleanField,
    DateTimeField,
    Document,
    IntField,
    ListField,
    StringField,
)
from mongoengine.queryset.visitor import Q
from pydantic import BaseModel, Field

from nomad import utils
from nomad.atomutils import Formula
from nomad.cli.admin.springer import normalize_formula, parse_springer_entry
from nomad.config import config
from nomad.processing.base import app

logger = utils.get_logger(__name__)

router = APIRouter()


class APITag(str, Enum):
    DEFAULT = 'resources'


# TODO generate list from optimade api
optimade_providers = {
    'https://www.crystallography.net/cod/optimade/v1/': dict(
        name='Crystallography Open Database',
        ref_url=lambda x: f'https://www.crystallography.net/cod/{x["entry_id"]}.html',
    ),
    'https://optimade.materialsproject.org/v1/': dict(
        name='The Materials Project',
        ref_url=lambda x: f'https://materialsproject.org/materials/{x["entry_id"]}',
    ),
    'https://aiida.materialscloud.org/mc3d-structures/optimade/v1/': dict(
        name='Materials Cloud',
        ref_url=lambda x: f'https://www.materialscloud.org/discover/mc3d/details/{x["chemical_formula_reduced"]}',
    ),
    'https://oqmd.org/optimade/v1/': dict(
        name='OQMD',
        ref_url=lambda x: None
        if x.get('oqmd_id') is None
        else f'https://oqmd.org/materials/entry/{x["oqmd_id"]}',
    ),
    # jarvis search does not seem to work, it gives out all structures
    # 'https://jarvis.nist.gov/optimade/jarvisdft/v1/': dict(
    #     name='Joint Automated Repository for Various Integrated Simulations',
    #     ref_url=lambda x: x['entry'].get('attributes', {}).get('reference')
    # ),
    'https://api.mpds.io/v1/': dict(
        name='Materials Platform for Data Science',
        ref_url=lambda x: f'https://mpds.io/#entry/{x["entry_id"]}',
    ),
    'https://optimade.odbx.science/v1/': dict(
        name='Open Database of Xtals',
        ref_url=lambda x: f'https://odbx.science/structures/{x["entry_id"]}',
    ),
    'https://www.crystallography.net/tcod/optimade/v1/': dict(
        name='Theoretical Crystallography Open Database',
        ref_url=lambda x: f'https://www.crystallography.net/tcod/{x["entry_id"]}.html',
    ),
    'http://optimade.2dmatpedia.org/v1/': dict(
        name='2DMatpedia',
        ref_url=lambda x: f'http://2dmatpedia.org/2dmaterials/doc/{x["entry_id"]}',
    ),
    # aflow does not seem to work
    # 'https://aflow.org/API/optimade/v1/': dict(
    #     name='Automatic-FLOW Computational Materials Data Repository',
    #     ref_url=lambda x: None
    # )
}

optimade_dbs: list[str] = [
    str(details['name']) for details in optimade_providers.values()
]

no_url_found = '__no_url_found'

status_db = '__status__'

aflow_prototypes_db = 'Aflow prototypes'

springer_materials_db = 'Springer Materials'

aflow_home_url = 'http://aflowlib.org/prototype-encyclopedia'

springer_materials_home_url = 'http://materials.springer.com'

comments = {
    aflow_prototypes_db: """
    Reference to the prototype structure in the Aflow encyclopedia of crystallographic
    prototypes.
    """,
    springer_materials_db: """
    Reference to the entry in the Springer Materials Inorganic Solid Phases database.
    """,
}
comments.update(
    {
        db: f"""
Reference to the entry in the {db} database queried using the Optimade API.
"""
        for db in optimade_dbs
    }
)


space_groups = (
    ['triclinic'] * 2
    + ['monoclinic'] * 13
    + ['orthorhombic'] * 59
    + ['tetragonal'] * 68
    + ['trigonal'] * 25
    + ['hexagonal'] * 27
    + ['cubic'] * 36
)


spaces_re = re.compile(r'\s+')
search_re = re.compile(' href="(/isp/[^"]+)')
formula_re = re.compile(r'([A-Z][a-z]?)([0-9.]*)|\[(.*?)\]([0-9]+)')
elements_re = re.compile(r'[A-Z][a-z]*')
prototype_re = re.compile(r'\<a +href="(A.+?)\.html"\>')
wyckoff_re = re.compile(r'\\left\(\d+([a-z])\\right\)')


class Resource(Document):
    id = StringField(primary_key=True)
    url = StringField()
    database_name = StringField()
    database_version = StringField()
    chemical_formula = StringField()
    wyckoff_letters = ListField()
    download_time = DateTimeField()
    is_updating = BooleanField(default=False)
    # TODO determine if saving the data is necessary, it is too much for the mongo db
    # data = DictField()
    available_data = ListField()
    space_group_number = IntField()
    n_sites = IntField()
    meta = {
        'db_alias': 'resources',
        'indexes': [
            'chemical_formula',
            'wyckoff_letters',
            'database_name',
            'space_group_number',
            'n_sites',
        ],
    }


class ResourceModel(BaseModel):
    # data: Dict[str, Any] = Field(
    #     {}, description=''' Value of the data referenced by the entry.
    #     ''')
    available_data: list[str] = Field(
        [], description="""List of available data referenced by the entry"""
    )
    url: str = Field(
        None,
        description="""
        URL of the entry in the database.
        """,
    )
    id: str = Field(
        None,
        description="""
        Name to identify the referenced data.
        """,
    )
    download_time: datetime = Field(
        None,
        description="""
        Date the data was downloaded.
        """,
    )
    database_name: str | None = Field(
        None,
        description="""
        Name to identify the referenced data.
        """,
    )
    kind: str | None = Field(
        None,
        description="""
        Kind of the reference data, e.g. journal, online, book.
        """,
    )
    comment: str | None = Field(
        None,
        description="""
        Annotations on the reference.
        """,
    )
    database_version: str | None = Field(
        None,
        description="""
        Version of the database.
        """,
    )
    # TODO include homepage, assign version and comment

    @classmethod
    def _get_value(cls, v: Any, to_dict: bool, **kwargs) -> Any:
        if to_dict:
            return dict(v) if isinstance(v, dict) else v
        return super()._get_value(v, to_dict=to_dict, **kwargs)


class ResourcesModel(BaseModel):
    data: list[ResourceModel] = Field(
        [], description='The list of resources, currently in our database.'
    )

    is_retrieving_more: bool = Field(
        False,
        description='Indicates that NOMAD is currently potentially adding more resources.',
    )


async def _download(session: httpx.AsyncClient, path: str) -> httpx.Response:
    n_retries = 0
    while True:
        try:
            response = await session.get(path, follow_redirects=True)
            if response.status_code == 200:
                return response
        except Exception as e:
            logger.error(
                'Cannot use http to download related resource data', exc_info=e
            )
        n_retries += 1
        if n_retries > config.resources.download_retries:
            break
        await asyncio.sleep(config.resources.download_retry_delay)
    return None


def _update_dict(target: dict[str, float], source: dict[str, float]):
    for key, val in source.items():
        if key in target:
            target[key] += val
        else:
            target[key] = val


def _components(formula_str: str, multiplier: float = 1.0) -> dict[str, float]:
    # match atoms and molecules (in brackets)
    components = formula_re.findall(formula_str)

    symbol_amount: dict[str, float] = {}
    for component in components:
        element, amount_e, molecule, amount_m = component
        if element:
            if not amount_e:
                amount_e = 1.0
            _update_dict(symbol_amount, {element: float(amount_e) * multiplier})

        elif molecule:
            if not amount_m:
                amount_m = 1.0
            _update_dict(
                symbol_amount, _components(molecule, float(amount_m) * multiplier)
            )

    return symbol_amount


def parse_aflow_prototype(text: str) -> dict[str, Any]:
    """
    Parse information from aflow prototype structure entry.
    """
    soup = bs4.BeautifulSoup(text, 'html.parser')
    results = dict()
    tds = soup.find_all('td')
    for n, item in enumerate(tds):
        if item.find_all('strong'):
            results[item.get_text()] = tds[n + 2].get_text()
    return results


async def _get_urls_aflow_prototypes(
    session: httpx.AsyncClient, space_group_number: int
) -> list[str]:
    if space_group_number is None or space_group_number == 0:
        return []

    response = await _download(
        session,
        f'{aflow_home_url}/{space_groups[space_group_number - 1]}_spacegroup.html',
    )
    if response is None:
        return []

    urls = []
    for path in prototype_re.findall(response.text):
        match = re.search(r'_(\d+)_', path)
        space_group_number_path = int(match.group(1)) if match else 0
        if space_group_number_path != space_group_number:
            continue
        urls.append(f'{aflow_home_url}/{path}.html')
    return urls


async def _get_resources_aflow_prototypes(
    session: httpx.AsyncClient, path: str, chemical_formula: str
) -> list[Resource]:
    response = await _download(session, path)
    if response is None:
        return []

    resource = Resource()
    resource.database_name = aflow_prototypes_db
    wyckoff_letters_data = wyckoff_re.findall(response.text)
    resource.n_sites = len(wyckoff_letters_data)
    wyckoff_letters_data = list(set(wyckoff_letters_data))
    wyckoff_letters_data.sort()
    # compare wyckoff with input
    resource.url = path
    data = parse_aflow_prototype(response.text)
    prototype_label = data.get('AFLOW prototype label', '')
    resource.id = prototype_label
    resource.space_group_number = int(data.get('Space group number', 0))
    resource.wyckoff_letters = wyckoff_letters_data
    # chemical formula should correspond to the chemical formula of the entry not the prototype
    resource.chemical_formula = chemical_formula
    # generate structure info
    response = await _download(session, f'{aflow_home_url}/CIF/{prototype_label}.cif')
    if response is not None:
        structure_file = io.StringIO()
        structure_file.write(response.text)
        structure_file.seek(0)
        atoms = ase.io.read(structure_file, format='cif')
        data['lattice_vectors'] = atoms.get_cell().tolist()
        data['atom_positions'] = atoms.get_positions().tolist()
        data['atom_labels'] = atoms.get_chemical_symbols()
    # resource.data = data
    resource.available_data = list(data.keys())
    resource.download_time = datetime.now()
    resource.save()
    return [resource]


async def _get_urls_springer_materials(
    session: httpx.AsyncClient, chemical_formula: str
) -> list[str]:
    if chemical_formula is None:
        return []

    elements = list(set(elements_re.findall(chemical_formula)))
    elements.sort()
    elements_str = '-'.join(elements)
    page = 1
    urls = []
    while True:
        url = f'{springer_materials_home_url}/search?searchTerm=es:{elements_str}&pageNumber={page}&datasourceFacet=sm_isp&substanceId='
        response = await _download(session, url)
        if response is None:
            logger.error(
                'Error accessing urls from springer materials.', data=dict(url=url)
            )
            break
        page += 1
        paths = search_re.findall(response.text)
        if not paths:
            break
        for path in paths:
            urls.append(f'{springer_materials_home_url}{path}')

    return urls


async def _get_resources_springer_materials(
    session: httpx.AsyncClient, path: str
) -> list[Resource]:
    resource = Resource()
    resource.url = path
    resource.id = os.path.basename(path)
    resource.database_name = springer_materials_db
    response = await _download(session, path)
    if response is None:
        logger.error(
            f'Error accessing springer materials resource.', data=dict(path=path)
        )
        return [resource]
    try:
        # we need to query individual entry ONLY to get spacegroup!
        # TODO find a way to limit springer search to particular spacegroup so
        # we do not need to access individual entries
        data = parse_springer_entry(response.text)
    except Exception:
        data = dict()
    space_group_number = data.get('space_group_number', '0')
    resource.space_group_number = (
        int(space_group_number) if space_group_number.isdecimal() else None
    )
    resource.chemical_formula = data.get('normalized_formula')
    # resource.data = data
    resource.available_data = list(data.keys())
    resource.database_version = data.get('version')
    resource.download_time = datetime.now()
    resource.save()
    return [resource]


async def _get_urls_optimade(
    chemical_formula_hill: str,
    chemical_formula_reduced: str,
    providers: list[str] = None,
) -> list[str]:
    filter_hill = (
        f'chemical_formula_hill = "{chemical_formula_hill}"'
        if chemical_formula_hill is not None
        else None
    )
    filter_reduced = (
        f'chemical_formula_reduced = "{chemical_formula_reduced}"'
        if chemical_formula_reduced is not None
        else None
    )

    if providers is None:
        providers = list(optimade_providers.keys())
    else:
        providers = [
            key for key, val in optimade_providers.items() if val['name'] in providers
        ]

    urls = []
    for base_url in providers:
        query = (
            filter_hill
            if base_url.startswith('https://www.crystallography.net/')
            else filter_reduced
        )
        if query is None:
            continue
        urls.append(f'{base_url}structures?filter={query}&response_format=json')
    return urls


async def _get_resources_optimade(
    session: httpx.AsyncClient, path: str
) -> list[Resource]:
    response = await _download(session, path)
    if response is None:
        logger.error(f'Error accessing optimade resources.', data=dict(path=path))
        return []
    data = response.json()
    resources: list[Resource] = []
    meta = data.get('meta', dict())
    provider = meta.get('provider', dict()).get('name', '')
    base_url = path.split('structures?filter')[0]
    ref_url = optimade_providers[base_url]['ref_url']
    for entry in data.get('data', []):
        entry_id = entry.get('id')
        params = dict(
            entry_id=entry.get('id'),
            chemical_formula_reduced=data.get('chemical_formula_reduced', ''),
            oqmd_id=entry.get('attributes', {}).get('_oqmd_entry_id'),
            entry=entry,
        )
        resource = Resource()
        # resolve provider-specific path to entry in respective database
        resource.url = ref_url(params)  # type: ignore
        resource.database_name = provider
        resource.id = f'{entry_id}'
        attributes = entry.pop('attributes', dict())
        chemical_formula = attributes.get('chemical_formula_hill')
        if chemical_formula is None:
            chemical_formula = attributes.get('chemical_formula_reduced', '')
        resource.chemical_formula = normalize_formula(chemical_formula)
        resource.download_time = datetime.now()
        resource.database_version = meta.get('api_version')
        # flatten entry data
        entry.update({key: val for key, val in attributes.items()})
        # resource.data = entry
        resource.available_data = list(entry.keys())
        resource.save()
        resources.append(resource)
    return resources


@app.task
def retrieve_resources(
    status_resource_id,
    urls_to_ignore: list[str],
    space_group_number,
    chemical_formula,
    chemical_formula_hill,
    chemical_formula_reduced,
    wyckoff_letters,
    n_sites,
):
    urls_to_ignore_as_set = set(urls_to_ignore)

    async def _retrieve_resources():
        limits = httpx.Limits(max_connections=config.resources.max_connections)
        async with httpx.AsyncClient(limits=limits) as session:
            # get urls from sources
            aflow_task = asyncio.create_task(
                _get_urls_aflow_prototypes(session, space_group_number)
            )
            springer_task = asyncio.create_task(
                _get_urls_springer_materials(session, chemical_formula)
            )
            optimade_task = asyncio.create_task(
                _get_urls_optimade(
                    chemical_formula_hill, chemical_formula_reduced, optimade_dbs
                )
            )

            aflow_urls: list[str]
            springer_urls: list[str]
            optimade_urls: list[str]
            aflow_urls, springer_urls, optimade_urls = await asyncio.gather(
                aflow_task, springer_task, optimade_task
            )

            # get resource(s) corresponding to each url
            tasks = []
            tasks.extend(
                [
                    asyncio.create_task(
                        _get_resources_aflow_prototypes(session, url, chemical_formula)
                    )
                    for url in aflow_urls
                    if url not in urls_to_ignore_as_set
                ]
            )
            tasks.extend(
                [
                    asyncio.create_task(_get_resources_springer_materials(session, url))
                    for url in springer_urls
                    if url not in urls_to_ignore_as_set
                ]
            )
            tasks.extend(
                [
                    asyncio.create_task(_get_resources_optimade(session, url))
                    for url in optimade_urls
                    if url not in urls_to_ignore_as_set
                ]
            )

            await asyncio.gather(*tasks)

    try:
        with start_blocking_portal() as portal:
            portal.call(_retrieve_resources)
    finally:
        status_resource = Resource.objects(id=status_resource_id).first()
        status_resource.download_time = datetime.now()
        status_resource.is_updating = False
        status_resource.save()


@router.get(
    '/',
    tags=[APITag.DEFAULT],
    summary='Get a list of external resources.',
    response_model=ResourcesModel,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_resources(
    space_group_number: int = FastApiQuery(None),
    wyckoff_letters: list[str] = FastApiQuery(None),
    n_sites: int = FastApiQuery(None),
    chemical_formula_reduced: str = FastApiQuery(None),
):
    """
    Get all external resources that match a specific query
    """

    chemical_formula_hill, chemical_formula = None, None
    if chemical_formula_reduced is not None:
        formula = Formula(chemical_formula_reduced)
        chemical_formula_hill = formula.format('hill')
        chemical_formula = normalize_formula(chemical_formula_hill)
    else:
        chemical_formula_hill = None
        chemical_formula = None
    if wyckoff_letters is not None:
        wyckoff_letters = list(set(wyckoff_letters))
        wyckoff_letters.sort()

    sources: dict[str, int] = dict()

    def convert_resources_to_models(resources) -> list[ResourceModel]:
        data: list[ResourceModel] = []
        additional_data: list[ResourceModel] = []
        for resource in resources:
            if (
                resource is None
                or resource.url is None
                or resource.id is None
                or resource.id.startswith(no_url_found)
            ):
                continue
            database = resource.database_name
            sources.setdefault(database, 0)
            sources[database] += 1
            # show the first five results from each resource and the rest we append later
            model = ResourceModel(
                url=resource.url,
                id=resource.id,
                available_data=resource.available_data,
                database_name=resource.database_name,
                download_time=resource.download_time,
                database_version=resource.database_version,
                comment=comments.get(database),
            )
            if sources[database] <= 5:
                data.append(model)
            else:
                additional_data.append(model)

        return data + additional_data

    query_aflow = Q(
        chemical_formula=chemical_formula,
        space_group_number=space_group_number,
        wyckoff_letters=wyckoff_letters,
        n_sites=n_sites,
        database_name=aflow_prototypes_db,
    )
    query_springer = Q(
        chemical_formula=chemical_formula,
        space_group_number=space_group_number,
        database_name=springer_materials_db,
    )
    query_optimade = Q(
        chemical_formula=chemical_formula, database_name__in=optimade_dbs
    )
    resources = Resource.objects(query_aflow | query_springer | query_optimade)

    status_resource = Resource.objects(
        chemical_formula=chemical_formula,
        space_group_number=space_group_number,
        wyckoff_letters=wyckoff_letters,
        n_sites=n_sites,
        database_name=status_db,
    ).first()

    trigger_refresh = False
    if not status_resource:
        status_resource = Resource(
            id=utils.create_uuid(),
            chemical_formula=chemical_formula,
            space_group_number=space_group_number,
            wyckoff_letters=wyckoff_letters,
            n_sites=n_sites,
            database_name=status_db,
            download_time=datetime.now(),
            is_updating=True,
        )
        trigger_refresh = True

    if not status_resource.is_updating:
        delta_time = datetime.now() - status_resource.download_time
        if delta_time.total_seconds() > config.resources.max_time_in_mongo:
            trigger_refresh = True

    existing_resources = []
    existing_urls = set()
    for resource in resources:
        delta_time_db = datetime.now() - resource.download_time
        if delta_time_db.total_seconds() > config.resources.max_time_in_mongo:
            resource.delete()
            continue

        existing_resources.append(resource)
        existing_urls.add(resource.url)

    existing_models = convert_resources_to_models(existing_resources)

    if trigger_refresh:
        status_resource.is_updating = True
        status_resource.save()

        retrieve_resources.apply_async(
            [
                status_resource.id,
                list(existing_urls),
                space_group_number,
                chemical_formula,
                chemical_formula_hill,
                chemical_formula_reduced,
                wyckoff_letters,
                n_sites,
            ]
        )

    return ResourcesModel(
        data=existing_models, is_retrieving_more=status_resource.is_updating
    )
