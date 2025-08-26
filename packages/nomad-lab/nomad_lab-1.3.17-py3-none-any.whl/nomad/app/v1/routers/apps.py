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

import fnmatch
import re
from enum import Enum
from typing import Any

import jmespath
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from nomad.app.v1.models import HTTPExceptionModel
from nomad.app.v1.models.pagination import Pagination
from nomad.app.v1.utils import create_responses
from nomad.config import config
from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import (
    Menu,
    MenuItemHistogram,
    MenuItemNestedObject,
    MenuItemPeriodicTable,
    MenuItemTerms,
    WidgetHistogram,
    WidgetPeriodicTable,
    WidgetScatterPlot,
    WidgetTerms,
)
from nomad.datamodel import EntryArchive
from nomad.metainfo.elasticsearch_extension import Elasticsearch, entry_type

# Compile the regex once at module load time.
SCHEMA_REGEX = re.compile(r'#[a-zA-Z0-9_.#]+')
_bad_app_not_found = (
    status.HTTP_404_NOT_FOUND,
    {
        'model': HTTPExceptionModel,
        'description': 'Could not find an app with the path "{app_path}".',
    },
)
_bad_search_quantity_parse = (
    status.HTTP_422_UNPROCESSABLE_ENTITY,
    {
        'model': HTTPExceptionModel,
        'description': 'Could not load or parse the requested search quantity.',
    },
)


class APITag(str, Enum):
    DEFAULT = 'apps'


router = APIRouter()

# Caches for entry point apps and search quantities
app_entry_points_cache: dict[str, AppEntryPoint] = {}
app_cache: dict[str, dict[str, Any]] = {}
app_search_quantity_cache: dict[str, list['SearchQuantity']] = {}
all_search_quantities: dict[str, 'SearchQuantity'] = {}


class SearchQuantity(BaseModel):
    quantity: str = Field(description='Name of the search quantity.')
    quantity_normalized: str = Field(
        ...,
        description='The name of the quantity normalized for queries.',
        exclude=True,
    )
    description: str | None = Field(
        None, description='Description of the search quantity.'
    )
    dtype: str | None = Field(None, description='Type of the search quantity.')
    unit: str | None = Field(None, description='Unit of the search quantity.')
    shape: str | None = Field(None, description='Shape of the search quantity.')
    aliases: list[str] | None = Field(
        None, description='Aliases for the search quantity.'
    )
    aggregatable: bool = Field(
        False, description='Whether the search quantity is aggregatable.'
    )
    dynamic: bool = Field(False, description='Whether the search quantity is dynamic.')
    repeats: bool = Field(False, description='Whether the search quantity repeats.')
    nested: bool = Field(
        False, description='Whether the search quantity is inside a nested object.'
    )


class SearchQuantityQuery(BaseModel):
    input: str | None = Field(
        None,
        description='The input used for filtering down the returned search quantitities',
    )
    dtype: str | list[str] | None = Field(
        None, description='The data type of the search quantity.'
    )
    aggregatable: bool | None = Field(
        None, description='Whether the search quantity is aggregatable.'
    )


class SearchQuantityRequest(BaseModel):
    app_path: str | None = Field(
        None,
        description='Path of the app in which the search quantities should be searched for.',
    )
    query: SearchQuantityQuery = Field(
        SearchQuantityQuery(),
        description='Query for filtering search quantities.',
    )
    pagination: Pagination = Field(description='Controls the pagination of the values.')


class DataType(Enum):
    INT = 'int'
    FLOAT = 'float'
    TIMESTAMP = 'timestamp'
    STRING = 'string'
    ENUM = 'enum'
    BOOLEAN = 'boolean'
    UNKNOWN = 'unknown'


def get_datatype(type_obj) -> DataType:
    """
    Converts a metainfo data type object to a simplified string representation.

    Args:
        type_obj (Any): The data type object.

    Returns:
        DataType: Simplified data type value.
    """
    type_data = (
        type_obj.get('type_data') if type_obj and isinstance(type_obj, dict) else None
    )
    type_kind = (
        type_obj.get('type_kind') if type_obj and isinstance(type_obj, dict) else None
    )

    if isinstance(type_data, str) and 'int' in type_data:
        return DataType.INT
    elif isinstance(type_data, str) and 'float' in type_data:
        return DataType.FLOAT
    elif type_data in [
        'nomad.metainfo.metainfo._Datetime',
        'nomad.metainfo.data_type.Datetime',
    ]:
        return DataType.TIMESTAMP
    elif type_data == 'str':
        return DataType.STRING
    elif isinstance(type_kind, str) and type_kind.lower() == 'enum':
        return DataType.ENUM
    elif type_data == 'bool':
        return DataType.BOOLEAN
    else:
        return DataType.UNKNOWN


def parse_jmespath(input: str) -> dict[str, Any]:
    """
    Parses a JMESPath expression and extracts the targeted quantity along with additional details.
    """
    match = SCHEMA_REGEX.search(input)
    schema = ''
    path = input
    if match:
        schema = match.group(0)
        path = input[: match.start()] + input[match.end() :]

    try:
        ast = jmespath.compile(path).parsed
    except Exception as e:
        return {
            'quantity': None,
            'path': None,
            'extras': None,
            'error': str(e),
            'schema': '',
        }

    def recurse_ast(node):
        type_ = node.get('type')
        name = node.get('name')
        children = node.get('children', [])
        field, extras = [], []
        if children:
            child_fields, child_extras = [], []
            for child in children:
                cf, ce = recurse_ast(child)
                child_fields.append(cf)
                child_extras.append(ce)
            if type_ == 'filter_projection':
                for cf in child_fields[:2]:
                    field.extend(cf)
                extras.append(child_fields[0] + child_fields[2])
            elif type_ == 'function' and name == 'min_by':
                field.extend(child_fields[0])
                extras.append(child_fields[0] + child_fields[1])
            else:
                for cf in child_fields:
                    field.extend(cf)
                for ce in child_extras:
                    extras.extend(ce)
        elif type_ == 'field':
            return [node['value']], extras
        return field, extras

    field, extras_list = recurse_ast(ast)
    quantity = '.'.join(field) + schema
    extras = ['.'.join(x) + schema for x in extras_list]
    return {
        'quantity': quantity,
        'extras': extras,
        'path': path,
        'schema': schema,
        'error': None,
    }


def normalize_name(input: str) -> str:
    """
    Normalizes the input string.
    """
    return input.replace('_', ' ').replace('.', ' ').replace(' ', '').lower()


def get_search_quantity(
    search_quantity, name: str, is_section: bool = False, repeats: bool = False
) -> SearchQuantity:
    """
    Constructs a SearchQuantity object from metadata.
    """
    if is_section:
        keys = ['description', 'nested', 'repeats']
        metadict = search_quantity.sub_section.m_to_dict(with_meta=True)
        instanceMeta = search_quantity.m_to_dict(with_meta=True)
        metadict['repeats'] = repeats or instanceMeta.get('repeats')
        es_annotations = search_quantity.m_get_annotations(Elasticsearch, as_list=True)
        metadict['nested'] = any(x.nested for x in es_annotations)
    else:
        keys = [
            'description',
            'dtype',
            'unit',
            'shape',
            'aliases',
            'aggregatable',
            'dynamic',
            'repeats',
        ]
        metadict = search_quantity.definition.m_to_dict(with_meta=True)
        metadict['aggregatable'] = search_quantity.aggregatable
        metadict['dynamic'] = search_quantity.dynamic
        metadict['repeats'] = search_quantity.repeats
        metadict['dtype'] = get_datatype(metadict['type'])
    result = SearchQuantity(quantity=name, quantity_normalized=normalize_name(name))
    for key in keys:
        val = metadict.get(key)
        if val is not None:
            setattr(result, key, val)
    return result


def glob(path: str, include: list[str], exclude: list[str]) -> bool:
    """
    Determines if path matches include and not exclude.
    """
    match = False if include else True
    for pattern in include or []:
        if fnmatch.fnmatch(path, pattern):
            match = True
            break
    for pattern in exclude or []:
        if fnmatch.fnmatch(path, pattern):
            match = False
            break
    return match


def prefilter_search_quantities(
    search_quantities: dict[str, SearchQuantity], app_path: str
) -> list[SearchQuantity]:
    """Pre-filters for a specific app based on its entry point."""
    entry_point = app_entry_points_cache.get(app_path)
    sq_filter = entry_point.app.search_quantities
    return [
        sq
        for key, sq in search_quantities.items()
        if glob(key, sq_filter.include, sq_filter.exclude)
    ]


def match_search_quantities(
    search_quantities: list[SearchQuantity], query: SearchQuantityQuery
) -> list[SearchQuantity]:
    """Filters and sorts search quantities."""
    dtypes = (
        {query.dtype}
        if isinstance(query.dtype, str)
        else set(query.dtype)
        if query.dtype
        else None
    )
    input_norm = normalize_name(query.input) if query.input else None
    filtered = [
        sq
        for sq in search_quantities
        if (dtypes is None or sq.dtype in dtypes)
        and (query.aggregatable is None or query.aggregatable == sq.aggregatable)
        and (input_norm is None or input_norm in sq.quantity_normalized)
    ]
    if query.input:
        filtered.sort(key=lambda sq: len(sq.quantity) - len(query.input))
    return filtered


def _lazy_build_search_quantities():
    """Lazy-Populate entry point cache and all_search_quantities."""
    # entry points
    for entry_point in config.plugins.entry_points.filtered_values():
        if isinstance(entry_point, AppEntryPoint):
            app_entry_points_cache[entry_point.app.path] = entry_point
    # base quantities
    all_search_quantities.clear()
    for key, value in entry_type.quantities.items():
        if not value.annotation.suggestion:
            all_search_quantities[key] = get_search_quantity(value, key)

    # section quantities
    def _get_sections(m_def, prefix=None, repeats=False):
        for sub in m_def.all_sub_sections.values():
            name = f'{prefix}.{sub.name}' if prefix else sub.name
            info = get_search_quantity(sub, name, True, repeats)
            all_search_quantities[name] = info
            _get_sections(sub.sub_section, name, info.repeats)

    _get_sections(EntryArchive.results.sub_section, 'results')


# without this, the dictionary will be built once at import time—before the Elasticsearch extension had
# finished registering all of its entry_type.quantities, so it remained partially filled
def _ensure_initialized():
    if not all_search_quantities:
        _lazy_build_search_quantities()


@router.get(
    '/entry-points',
    tags=[APITag.DEFAULT],
    summary='Get all apps',
    response_model=dict[str, Any],
    response_model_exclude_none=True,
)
async def get_entry_points():
    """Entry point for getting information about all apps"""
    _ensure_initialized()
    apps = []
    for id, ep in app_entry_points_cache.items():
        app = ep.app.dict()
        app['id'] = id
        apps.append(app)
    return {'data': apps}


@router.get(
    '/entry-points/{app_path}',
    tags=[APITag.DEFAULT],
    summary='Get a specific app',
    response_model=dict[str, Any],
    response_model_exclude_none=True,
    responses=create_responses(_bad_app_not_found, _bad_search_quantity_parse),
)
async def get_entry_point(app_path: str):
    """Entry point for getting information about a specific app"""
    _ensure_initialized()
    if app_path in app_cache:
        return app_cache[app_path]
    entry_point = app_entry_points_cache.get(app_path)
    if entry_point is None:
        raise HTTPException(
            status_code=404, detail=f'Could not find an app with the path "{app_path}".'
        )
    search_quantities: dict[str, Any] = {}
    app = entry_point.app

    def add_jmespath(name: str, location: str = None):
        data = parse_jmespath(name)
        if data['error']:
            raise HTTPException(
                status_code=422,
                detail=f'Could not parse the search quantity "{name}" defined in {location}.',
            )
        for q in [data['quantity']] + data['extras']:
            add_search(q, location)

    def add_search(name: str, location: str = None):
        if name in search_quantities:
            return
        sq = all_search_quantities.get(name)
        if sq is None:
            raise HTTPException(
                status_code=422,
                detail=f'Could not load the search quantity "{name}" defined in {location}.',
            )
        search_quantities[name] = sq.dict()

    # columns
    for column in app.columns or []:
        add_jmespath(column.search_quantity, 'the results table as a column')
    # widgets
    if app.dashboard and app.dashboard.widgets:
        for widget in app.dashboard.widgets:
            if isinstance(widget, (WidgetPeriodicTable | WidgetTerms)):
                add_search(widget.search_quantity)
            elif isinstance(widget, WidgetHistogram) and widget.x:
                qty = (
                    widget.x if isinstance(widget.x, str) else widget.x.search_quantity
                )
                add_search(qty)
            elif isinstance(widget, WidgetScatterPlot):
                if widget.x:
                    add_jmespath(
                        widget.x.search_quantity
                        if not isinstance(widget.x, str)
                        else widget.x,
                        'the x-axis of a scatter plot widget',
                    )
                if widget.y:
                    add_jmespath(
                        widget.y.search_quantity
                        if not isinstance(widget.y, str)
                        else widget.y,
                        'the y-axis of a scatter plot widget',
                    )
                if widget.markers and widget.markers.color:
                    cd = widget.markers.color
                    add_jmespath(
                        cd.search_quantity if not isinstance(cd, str) else cd,
                        'the marker color of a scatter plot widget',
                    )

    # menus
    def load_menu(menu: Menu | MenuItemNestedObject):
        for item in menu.items or []:
            if isinstance(item, Menu):
                load_menu(item)
            if isinstance(item, MenuItemNestedObject):
                add_search(item.path, 'a menu nested object item')
                load_menu(item)
            elif isinstance(item, MenuItemTerms):
                add_search(item.search_quantity, 'a menu terms item')
            elif isinstance(item, MenuItemHistogram):
                if isinstance(item.x, str):
                    add_search(item.x, 'a menu histogram item')
                else:
                    add_search(item.x.search_quantity, 'a menu histogram item')
            elif isinstance(item, MenuItemPeriodicTable):
                add_search(item.search_quantity, 'a menu periodic table item')

    if app.menu:
        load_menu(app.menu)
    # filters_locked
    for key in (app.filters_locked or {}).keys():
        add_search(key, 'filters_locked')

    response = {'app': entry_point.app.dict(), 'search_quantities': search_quantities}
    app_cache[app_path] = response
    return response


@router.post(
    '/search-quantities',
    tags=[APITag.DEFAULT],
    summary='Search and filter search quantities',
    response_model=list[SearchQuantity],
    response_model_exclude_none=True,
    responses=create_responses(_bad_app_not_found),
)
async def get_entry_point_search_quantities(data: SearchQuantityRequest):
    """Entry point for suggestions for search quantities"""
    _ensure_initialized()
    if data.app_path:
        if data.app_path not in app_entry_points_cache:
            raise HTTPException(
                status_code=404,
                detail=f'Could not find an app with the path "{data.app_path}".',
            )
        sqs = app_search_quantity_cache.get(data.app_path)
        if sqs is None:
            sqs = prefilter_search_quantities(all_search_quantities, data.app_path)
            app_search_quantity_cache[data.app_path] = sqs
    else:
        sqs = list(all_search_quantities.values())
    matched = match_search_quantities(sqs, data.query)
    page, size = data.pagination.page, data.pagination.page_size
    return matched[(page - 1) * size : page * size]
