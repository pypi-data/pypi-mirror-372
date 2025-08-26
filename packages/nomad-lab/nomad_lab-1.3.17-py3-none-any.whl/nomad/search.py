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
This module provides an interface to elasticsearch. Other parts of NOMAD must not
interact with elasticsearch to maintain a clear coherent interface and allow for change.

Currently NOMAD uses one entry index and two distinct materials indices. The entries
index is based on two different mappings, once used by the old flask api (v0) and one
used by the new fastapi api (v1). The mappings are used at the same time and the documents
are merged. Write operations (index, publish, edit, lift embargo, delete) are common; defined
here in the module ``__init__.py``. Read operations are different and
should be used as per use-case directly from the ``v0`` and ``v1`` submodules.

Most common functions also take an ``update_materials`` keyword arg with allows to
update the v1 materials index according to the performed changes. TODO this is only
partially implemented.
"""

import json
import math
from collections.abc import Callable, Generator, Iterable, Iterator
from enum import Enum
from typing import Any, cast

import elasticsearch.helpers
from elasticsearch.exceptions import RequestError, TransportError
from elasticsearch_dsl import A, Q, Search
from elasticsearch_dsl.query import Query as EsQuery
from pydantic import ValidationError

from nomad import datamodel, infrastructure, utils
from nomad.app.v1.models import models
from nomad.app.v1.models.models import (
    Aggregation,
    AggregationBase,
    AggregationPagination,
    AggregationResponse,
    AutoDateHistogramAggregation,
    AutoDateHistogramAggregationResponse,
    Bucket,
    BucketAggregation,
    Criteria,
    DateHistogramAggregation,
    DateHistogramAggregationResponse,
    HistogramAggregation,
    HistogramAggregationResponse,
    MetadataPagination,
    MetadataRequired,
    MetadataResponse,
    MinMaxAggregation,
    MinMaxAggregationResponse,
    Pagination,
    PaginationResponse,
    QuantityAggregation,
    Query,
    StatisticsAggregation,
    StatisticsAggregationResponse,
    TermsAggregation,
    TermsAggregationResponse,
    Value,
)
from nomad.config import config
from nomad.datamodel import AuthorReference, EntryArchive, EntryMetadata, UserReference
from nomad.groups import MongoUserGroup
from nomad.metainfo import Datetime, Package, Quantity
from nomad.metainfo.elasticsearch_extension import (
    DocumentType,
    Elasticsearch,
    Index,
    SearchQuantity,
    create_dynamic_quantity_annotation,
    entry_index,
    entry_type,
    index_entries,
    material_entry_type,
    material_type,
    nexus_prefix,
    parse_quantity_name,
    schema_separator,
    update_materials,
    yaml_prefix,
)
from nomad.utils.pydantic import CustomErrorWrapper

_metainfo_initialized = False


class AggType(str, Enum):
    """Enumeration for the different aggregation types."""

    TERMS = 'terms'
    MIN_MAX = 'min_max'
    HISTOGRAM = 'histogram'
    DATE_HISTOGRAM = 'date_histogram'
    AUTO_DATE_HISTOGRAM = 'auto_date_histogram'
    STATISTICS = 'statistics'


def update_by_query(
    update_script: str,
    query: Any = None,
    owner: str = None,
    user_id: str = None,
    index: str = None,
    refresh: bool = False,
    **kwargs,
):
    """
    Uses the given painless script to update the entries by given query.

    In most cases, the elasticsearch entry index should not be updated field by field;
    you should run `index` instead and fully replace documents from mongodb and
    archive files.

    This method provides a faster direct method to update individual fields, e.g. to quickly
    update fields for editing operations.
    """
    if query is None:
        query = {}

    es_query_normalized = normalize_api_query(cast(Query, query), doc_type=entry_type)
    owner_query = _owner_es_query(owner=owner, user_id=user_id, doc_type=entry_type)
    es_query_validated = _api_to_es_query(es_query_normalized, entry_type, owner_query)

    body = {
        'script': {'source': update_script, 'lang': 'painless'},
        'query': es_query_validated.to_dict(),
    }

    body['script'].update(**kwargs)

    try:
        result = infrastructure.elastic_client.update_by_query(
            body=body, index=config.elastic.entries_index
        )
    except TransportError as e:
        utils.get_logger(__name__).error(
            'es update_by_query script error',
            exc_info=e,
            es_info=json.dumps(e.info, indent=2),
        )
        raise SearchError(e)

    if refresh:
        _refresh()

    return result


def delete_by_query(
    query: dict,
    owner: str = None,
    user_id: str = None,
    update_materials: bool = False,
    refresh: bool = False,
):
    """
    Deletes all entries that match the given query.
    """
    if query is None:
        query = {}

    es_query_normalized = normalize_api_query(cast(Query, query), doc_type=entry_type)
    owner_query = _owner_es_query(owner=owner, user_id=user_id, doc_type=entry_type)
    es_query_validated = _api_to_es_query(es_query_normalized, entry_type, owner_query)

    body = {'query': es_query_validated.to_dict()}

    try:
        result = infrastructure.elastic_client.delete_by_query(
            body=body, index=config.elastic.entries_index
        )
    except TransportError as e:
        utils.get_logger(__name__).error(
            'es delete_by_query error', exc_info=e, es_info=json.dumps(e.info, indent=2)
        )
        raise SearchError(e)

    if refresh:
        _refresh()

    if update_materials:
        # TODO update the matrials index at least for v1
        pass

    return result


def refresh():
    """
    Refreshes the specified indices.
    """

    try:
        infrastructure.elastic_client.indices.refresh(
            index=config.elastic.entries_index
        )
    except TransportError as e:
        utils.get_logger(__name__).error(
            'es delete_by_query error', exc_info=e, es_info=json.dumps(e.info, indent=2)
        )
        raise SearchError(e)


_refresh = refresh


def index(
    entries: EntryArchive | list[EntryArchive],
    update_materials: bool = False,
    refresh: bool = False,
) -> dict[str, str]:
    """
    Index the given entries based on their archive. Either creates or updates the underlying
    elasticsearch documents. If an underlying elasticsearch document already exists it
    will be fully replaced. Returns a dictionary of the format {entry_id: error_message}
    for all entries that failed to index.
    """
    if not isinstance(entries, list):
        entries = [entries]

    errors = index_entries(entries, refresh=refresh or update_materials)
    if update_materials:
        index_materials(entries, refresh=refresh)
    return errors


def index_materials(entries: EntryArchive | list[EntryArchive], **kwargs):
    """
    Index the materials within the given entries based on their archive. The entries
    have to be indexed first.
    """

    if not isinstance(entries, list):
        entries = [entries]

    update_materials(entries=entries, **kwargs)


# TODO this depends on how we merge section metadata
def publish(entries: Iterable[EntryMetadata], index: str = None) -> int:
    """
    Publishes the given entries based on their entry metadata. Sets publishes to true,
    and updates most user provided metadata with a partial update. Returns the number
    of failed updates.
    """
    return update_metadata(
        entries, index=index, published=True, update_materials=True, refresh=True
    )


def update_metadata(
    entries: Iterable[EntryMetadata],
    index: str = None,
    update_materials: bool = False,
    refresh: bool = False,
    **kwargs,
) -> int:
    """
    Update all given entries with their given metadata. Additionally apply kwargs.
    Returns the number of failed updates. This is doing a partial update on the underlying
    elasticsearch documents.
    """

    def elastic_updates():
        for entry_metadata in entries:
            entry_archive = entry_metadata.m_parent
            if entry_archive is None:
                entry_archive = EntryArchive(metadata=entry_metadata)
            entry_doc = entry_type.create_index_doc(entry_archive)

            entry_doc.update(**kwargs)

            yield dict(
                doc=entry_doc,
                _id=entry_metadata.entry_id,
                _index=entry_index.index_name,
                _op_type='update',
            )

    updates = list(elastic_updates())
    _, failed = elasticsearch.helpers.bulk(
        infrastructure.elastic_client, updates, stats_only=True
    )
    failed = cast(int, failed)

    if update_materials:
        # TODO update the matrials index at least for v1
        pass

    if refresh:
        _refresh()

    return failed


def delete_upload(upload_id: str, refresh: bool = False, **kwargs):
    """
    Deletes the given upload.
    """
    delete_by_query(query=dict(upload_id=upload_id), **kwargs)

    if refresh:
        _refresh()


def delete_entry(entry_id: str, index: str = None, refresh: bool = False, **kwargs):
    """
    Deletes the given entry.
    """
    delete_by_query(query=dict(entry_id=entry_id), **kwargs)

    if refresh:
        _refresh()


class SearchError(Exception):
    pass


class AuthenticationRequiredError(Exception):
    pass


_entry_metadata_defaults = {
    quantity.name: quantity.default
    for quantity in datamodel.EntryMetadata.m_def.quantities  # pylint: disable=not-an-iterable
    if quantity.default not in [None, [], False, 0]
}

_all_author_quantities = [
    quantity.name
    for quantity in EntryMetadata.m_def.all_quantities.values()
    if isinstance(quantity.type, UserReference | AuthorReference)
]


def _api_to_es_required(
    required: MetadataRequired, pagination: MetadataPagination, doc_type: DocumentType
) -> tuple[list[str] | None, list[str] | None, bool]:
    """
    Translates an API include/exclude argument into the appropriate ES
    arguments. Note that certain fields cannot be excluded from the underlying
    ES call, but will be excluded in the response.
    """
    # Suggestion values are always excluded
    excludes = ['*__suggestion']
    includes = None
    requires_filtering = False

    def includes_dynamic(include):
        for pattern in [] if include is None else include:
            if pattern.startswith('data'):
                return True
        return False

    if required:
        # Validate quantities
        # TODO validate quantities with wildcards
        for list_ in [required.include, required.exclude]:
            for quantity in [] if list_ is None else list_:
                if '*' not in quantity:
                    validate_quantity(quantity, doc_type=doc_type, loc=['required'])

        if required.include is not None and pagination.order_by not in required.include:
            required.include.append(pagination.order_by)

        if required.exclude is not None and pagination.order_by in required.exclude:
            required.exclude.remove(pagination.order_by)

        if required.include is not None and doc_type.id_field not in required.include:
            required.include.append(doc_type.id_field)

        if required.exclude is not None and doc_type.id_field in required.exclude:
            required.exclude.remove(doc_type.id_field)

        if required.include:
            includes = list(required.include)

        # Searchable quantities must be included if dynamic quantities are
        # requested, and searchable quantities cannot be excluded because we use
        # that information to reconstruct the dynamic quantities. Note that we
        # only modify the underlying ES call without changing the API request
        # itself.
        # TODO: Handle exclude patterns starting with wildcard
        if includes_dynamic(includes):
            includes.append('search_quantities*')
            requires_filtering = True
        if required.exclude:
            for pattern in required.exclude:
                if pattern.startswith('search_quantities'):
                    requires_filtering = True
                else:
                    excludes.append(pattern)
        if includes_dynamic(excludes):
            requires_filtering = True

    return includes, excludes, requires_filtering


def _es_to_api_pagination(
    es_response,
    pagination: MetadataPagination,
    order_quantity: SearchQuantity,
    doc_type,
) -> PaginationResponse:
    """
    Translates an ES pagination response into a pagination response that is
    expected by the API.
    """
    next_page_after_value = None
    if (
        0 < len(es_response.hits) < es_response.hits.total.value
        and len(es_response.hits) >= pagination.page_size
    ):
        last = es_response.hits[-1]
        if order_quantity.search_field == doc_type.id_field:
            next_page_after_value = last[doc_type.id_field]
        else:
            # after_value is not necessarily the value stored in the field
            # itself: internally ES can perform the sorting on a different
            # value which is reported under meta.sort.
            after_value = last.meta.sort[0]
            next_page_after_value = f'{after_value}:{last[doc_type.id_field]}'

    # For dynamic YAML quantities the field name is normalized to not include
    # the data type
    request_pagination = pagination.dict()
    if order_quantity.dynamic:
        request_pagination['order_by'] = order_quantity.qualified_name

    return PaginationResponse(
        total=es_response.hits.total.value,
        next_page_after_value=next_page_after_value,
        **request_pagination,
    )


def _es_to_entry_dict(
    hit,
    requires_filtering: bool,
    include_patterns: list[str] | None,
    exclude_patterns: list[str] | None,
) -> dict[str, Any]:
    """
    Translates an ES hit response into a response data object that is expected
    by the API.
    """
    entry_dict = hit.to_dict()

    # Add metadata default values
    for key, value in _entry_metadata_defaults.items():
        if key not in entry_dict:
            if not utils.glob(key, include_patterns, exclude_patterns):
                continue
            entry_dict[key] = value

    # Delete author email
    for author_quantity in _all_author_quantities:
        authors = entry_dict.get(author_quantity)
        if authors is None:
            continue
        if isinstance(authors, dict):
            authors = [authors]
        for author in authors:
            if 'email' in author:
                del author['email']

    # The search_quantities field is mapped here into the return structure. This
    # mapping quickly becomes a bottle-neck in the whole query process, and that
    # is why it has been heavily optimized. # TODO: If this mapping on every
    # request gets too heavy, we could map the response into a non-indexed field
    # at indexing time.
    search_quantities = entry_dict.get('search_quantities')
    if search_quantities:
        valid_keys = (
            'float_value',
            'str_value',
            'int_value',
            'datetime_value',
            'bool_value',
        )
        sep = schema_separator
        glob_func = utils.glob
        rebuild_dict = utils.rebuild_dict
        logger = utils.get_logger(__name__)
        flattened = {}
        for sq in search_quantities:
            try:
                id_val = sq.get('id')
                path_archive = sq.get('path_archive')
                if id_val is None or path_archive is None:
                    continue

                if requires_filtering:
                    path_schema = id_val.split(sep, 1)[0]
                    if not glob_func(path_schema, include_patterns, exclude_patterns):
                        continue

                for key in valid_keys:
                    if key in sq:
                        flattened[path_archive] = sq[key]
                        break

            except Exception as e:
                logger.error(
                    'error mapping dynamic search quantity to entry dict',
                    exc_info=e,
                    extra={'search_quantity': sq},
                )
        entry_dict.update(rebuild_dict(flattened))

    # Here we do additional filtering that could not be done by ES directly
    # TODO: If we at some point don't need to return search_quantities at all,
    # this filtering could be replaced by the action of dropping the whole
    # search_quantities field and doing additional filtering for the constructed
    # dynamic quantities.
    if requires_filtering:
        entry_dict = utils.prune_dict(entry_dict, include_patterns, exclude_patterns)

    return entry_dict


def _owner_es_query(
    owner: str,
    user_id: str = None,
    doc_type: DocumentType = entry_type,
):
    def query(query_type='term', **kwargs):
        prefix = '' if doc_type == entry_type else 'entries.'
        query_dict = {(prefix + field): value for field, value in kwargs.items()}
        return Q(query_type, **query_dict)

    def viewers_query(user_id: str | None, *, force_groups: bool = False) -> Q:
        """Filter for user viewers and group viewers.

        force_groups: If true, add group filter even if user_id is None."""

        q = Q('match_none')

        if user_id is not None:
            q |= query(viewers__user_id=user_id)

        if user_id is not None or force_groups:
            user_group_ids = MongoUserGroup.get_ids_by_user_id(user_id)
            q |= query('terms', viewer_groups=user_group_ids)

        return q

    if owner == 'all':
        q = query(published=True)
        q |= viewers_query(user_id, force_groups=True)
    elif owner == 'public':
        q = query(published=True) & query(with_embargo=False)
    elif owner == 'visible':
        q = query(published=True) & query(with_embargo=False)
        q |= viewers_query(user_id, force_groups=True)
    elif owner == 'shared':
        if user_id is None:
            raise AuthenticationRequiredError(
                'Authentication required for owner value shared.'
            )
        q = viewers_query(user_id)
    elif owner == 'user':
        if user_id is None:
            raise AuthenticationRequiredError(
                'Authentication required for owner value user.'
            )
        q = query(main_author__user_id=user_id)
    elif owner == 'staging':
        if user_id is None:
            raise AuthenticationRequiredError(
                'Authentication required for owner value user'
            )
        q = query(published=False) & viewers_query(user_id)
    elif owner == 'admin':
        if user_id is None or not datamodel.User.get(user_id=user_id).is_admin:
            raise AuthenticationRequiredError(
                'This can only be used by the admin user.'
            )
        q = None
    elif owner is None:
        q = None
    else:
        raise KeyError('Unsupported owner value')

    if q is not None:
        return q

    return Q('match_all')


class QueryValidationError(Exception):
    def __init__(self, error, loc):
        self.errors = [CustomErrorWrapper(Exception(error), loc=loc)]


def get_quantity(definition, path, schema, doc_type):
    """Creates a SearchQuantity definition for the given quantity definition."""
    annotation = create_dynamic_quantity_annotation(definition, doc_type)
    qualified_name = f'{path}{schema_separator}{schema}' if schema else path
    quantity = SearchQuantity(annotation, qualified_name=qualified_name)
    return quantity


def get_definition(path):
    parts = path.split('.')
    package = Package.registry.get(parts.pop(0))
    root = None
    section_name = parts.pop(0)
    for section in package.section_definitions:
        if section.name == section_name:
            root = section
            break
    for i_part, part in enumerate(parts):
        if i_part == len(parts) - 1:
            root = root.all_quantities[part]
        else:
            root = root.all_sub_sections[part].sub_section
    return root


def validate_quantity(
    quantity_name: str, doc_type: DocumentType = None, loc: list[str] = None
) -> SearchQuantity:
    """
    Validates the given quantity name against the given document type.

    Returns:
        A metainfo elasticsearch extension SearchQuantity object.

    Raises: QueryValidationError
    """
    assert quantity_name is not None

    if doc_type == material_entry_type and not quantity_name.startswith('entries'):
        quantity_name = f'entries.{quantity_name}'

    if doc_type == material_type and quantity_name.startswith('entries'):
        doc_type = material_entry_type

    if doc_type is None:
        doc_type = entry_type

    # Primarily, look for the definition in the pre-registered static search
    # quantities.
    quantity = doc_type.quantities.get(quantity_name)

    if quantity is None:
        path, schema, dtype = parse_quantity_name(quantity_name)
        # Queries targeting YAML or nexus schema are translated into dynamic
        # quantity searches on the fly using the provided data type.
        if schema and schema.startswith((yaml_prefix, nexus_prefix)):
            datatype = {
                'int': int,
                'str': str,
                'float': float,
                'bool': bool,
                'datetime': Datetime,
            }.get(dtype)
            if not datatype:
                raise QueryValidationError(
                    (
                        f'Could not resolve the data type for quantity {quantity_name}. '
                        'Please include the data type in the quantity name using the '
                        '"#<type>" postfix.'
                    ),
                    loc=[quantity_name] if loc is None else loc,
                )
            quantity = get_quantity(Quantity(type=datatype), path, schema, doc_type)
        else:
            raise QueryValidationError(
                f'{quantity_name} is not a {doc_type} quantity',
                loc=[quantity_name] if loc is None else loc,
            )

    return quantity


def normalize_api_query(
    query: Query, doc_type: DocumentType, prefix: str = None
) -> Query:
    """
    Normalizes the given query. Should be applied before _api_to_es_query, which
    expects a normalized query. Normalization will
    - replace nested dicts with`models.And`, `models.Nested` instances
    - introduce `models.Nested` if necessary
    - replace dicts with `models.And` or 'models.Range' queries.

    After normalization there should be no dicts or `*:(any|all|none)` values in the query.
    """

    def normalize_criteria(name, value: models.CriteriaValue, prefix: str) -> Query:
        if prefix is not None:
            full_name = f'{prefix}.{name}'
        else:
            full_name = name

        prefixes = []
        name_wo_prefix = name
        nested_prefix = None

        # If targeting nested key, add the nested filter
        for nested_key in doc_type.nested_object_keys:
            if nested_key == prefix:
                continue

            if full_name.startswith(f'{nested_key}'):
                if prefix is None or not prefix.startswith(nested_key):
                    prefixes.append(nested_key)
                    name_wo_prefix = full_name[len(nested_key) + 1 :]
                    nested_prefix = nested_key

            if full_name == nested_key:
                break
        name = name_wo_prefix

        query: Query = None

        # Dictionaries that are not at the root level can either be range
        # queries, or else they are interpreted as a list of AND queries.
        if isinstance(value, dict):
            try:
                query = Criteria(name=name, value=models.Range(**value))
            except ValidationError:
                query = models.And(
                    **{
                        'and': [
                            normalize_criteria(
                                k if name == '' else f'{name}.{k}', v, nested_prefix
                            )
                            for k, v in value.items()
                        ]
                    }
                )

        else:
            query = Criteria(name=name, value=value)

        for rev_prefix in reversed(prefixes):
            query = models.Nested(prefix=rev_prefix, query=query)

        return query

    def normalize_query(query: Query):
        return normalize_api_query(query, doc_type=doc_type, prefix=prefix)

    if isinstance(query, dict):
        if len(query) is None:
            return models.Empty()

        if len(query) == 1:
            name = next(iter(query))
            return normalize_criteria(name, query[name], prefix)

        return models.And(
            **{
                'and': [
                    normalize_criteria(name, value, prefix)
                    for name, value in query.items()
                ]
            }
        )

    if isinstance(query, models.And):
        return models.And(**{'and': [normalize_query(op) for op in query.op]})

    if isinstance(query, models.Or):
        return models.Or(**{'or': [normalize_query(op) for op in query.op]})

    if isinstance(query, models.Not):
        return models.Not(**{'not': normalize_query(query.op)})

    if isinstance(query, models.Nested):
        return models.Nested(
            prefix=query.prefix,
            query=normalize_api_query(query, doc_type=doc_type, prefix=query.prefix),
        )

    if isinstance(query, models.Empty | models.Criteria):
        return query

    raise NotImplementedError(f'Query type {query.__class__} is not supported')


def remove_quantity_from_query(query: Query, quantity: str, prefix=None):
    """
    Removes all criteria with the given quantity from the query. Query has to be
    normalized. Remove is done by replacing respective criteria with an empty query.
    """

    if isinstance(query, models.And):
        return models.And(
            **{
                'and': [
                    remove_quantity_from_query(op, quantity, prefix) for op in query.op
                ]
            }
        )

    if isinstance(query, models.Or):
        return models.Or(
            **{
                'or': [
                    remove_quantity_from_query(op, quantity, prefix) for op in query.op
                ]
            }
        )

    if isinstance(query, models.Not):
        return models.Not(
            **{'not': remove_quantity_from_query(query.op, quantity, prefix)}
        )

    if isinstance(query, models.Nested):
        return models.Nested(
            prefix=query.prefix,
            query=remove_quantity_from_query(
                query.query, quantity, prefix=query.prefix
            ),
        )

    if isinstance(query, models.Empty):
        return query

    if isinstance(query, models.Criteria):
        name = query.name
        if prefix is not None:
            name = f'{prefix}.{name}'
        if name == quantity:
            return models.Empty()

        return query

    raise NotImplementedError(f'Query type {query.__class__} is not supported')


def _api_to_es_query(
    query: Query, doc_type: DocumentType, owner_query: EsQuery, prefix: str = None
) -> EsQuery:
    """
    Creates an ES query based on the API's query model. This needs to be a normalized
    query.

    However, this function performs validation of quantities and types and raises
    a QueryValidationError accordingly. This exception is populated with pydantic
    errors.

    Arguments:
        query: The api query object.
        doc_type:
            The elasticsearch metainfo extension document type that this query needs to
            be verified against.
        owner_query:
            A prebuild ES query that is added to nested entries query. Only for
            materials queries.
        prefix:
            An optional prefix that is added to all quantity names. Used for recursion.

    Returns:
        A elasticsearch dsl query object.

    Raises: QueryValidationError
    """

    def match(name: str, value: Value) -> EsQuery:
        if prefix is not None:
            name = f'{prefix}.{name}'

        if name == 'optimade_filter':
            value = str(value)
            from nomad.app.optimade import filterparser

            try:
                return filterparser.parse_filter(value, without_prefix=True)

            except filterparser.FilterException as e:
                raise QueryValidationError(
                    f'Could not parse optimade filter: {e}', loc=[name]
                )

        # TODO non keyword quantities, type checks
        quantity = validate_quantity(name, doc_type=doc_type)
        return quantity.get_query(value)

    def validate_query(query: Query) -> EsQuery:
        return _api_to_es_query(
            query, doc_type=doc_type, owner_query=owner_query, prefix=prefix
        )

    def validate_criteria(name: str, value: Any):
        if isinstance(value, models.All):
            return Q('bool', must=[match(name, item) for item in value.op])

        elif isinstance(value, models.Any_):
            return Q('bool', should=[match(name, item) for item in value.op])

        elif isinstance(value, models.None_):
            return Q('bool', must_not=[match(name, item) for item in value.op])

        elif isinstance(value, models.Range):
            if prefix is not None:
                name = f'{prefix}.{name}'
            quantity = validate_quantity(name, doc_type=doc_type)
            return quantity.get_range_query(value)

        elif isinstance(value, models.And | models.Or | models.Not):
            return validate_query(value)

        # list of values is treated as an "all" over the items
        elif isinstance(value, list):
            return Q('bool', must=[match(name, item) for item in value])

        elif isinstance(value, dict):
            raise NotImplementedError()

        else:
            return match(name, value)

    if isinstance(query, models.And):
        return Q('bool', must=[validate_query(operand) for operand in query.op])

    if isinstance(query, models.Or):
        return Q('bool', should=[validate_query(operand) for operand in query.op])

    if isinstance(query, models.Not):
        return Q('bool', must_not=validate_query(query.op))

    if isinstance(query, models.Nested):
        sub_doc_type = material_entry_type if query.prefix == 'entries' else doc_type
        sub_query = _api_to_es_query(
            query.query,
            doc_type=sub_doc_type,
            prefix=query.prefix,
            owner_query=owner_query,
        )

        if query.prefix == 'entries':
            sub_query &= owner_query

        return Q('nested', path=query.prefix, query=sub_query)

    if isinstance(query, models.Criteria):
        return validate_criteria(query.name, query.value)

    if isinstance(query, models.Empty):
        return Q()

    raise NotImplementedError(f'Query type {query.__class__} is not supported')


def validate_pagination(
    pagination: Pagination, doc_type: DocumentType, loc: list[str] = None
):
    order_quantity = None
    if pagination.order_by is not None:
        # When sorting by _score, or by _doc is requested, we create a dummy
        # order_quantity
        if pagination.order_by == '_score' or pagination.order_by == '_doc':
            dummy_annotation = Elasticsearch(
                definition=Quantity(type=float), doc_type=doc_type
            )
            order_quantity = SearchQuantity(dummy_annotation)
            order_quantity.search_field = pagination.order_by
        else:
            order_quantity = validate_quantity(
                pagination.order_by,
                doc_type=doc_type,
                loc=(loc if loc else []) + ['pagination', 'order_by'],
            )
            if not order_quantity.definition.is_scalar:
                raise QueryValidationError(
                    'the order_by quantity must be a scalar',
                    loc=(loc if loc else []) + ['pagination', 'order_by'],
                )

    page_after_value = pagination.page_after_value
    if (
        page_after_value is not None
        and pagination.order_by is not None
        and pagination.order_by != doc_type.id_field
        and ':' not in page_after_value
    ):
        pagination.page_after_value = f'{page_after_value}:'

    return order_quantity, page_after_value


def _api_to_es_sort(
    pagination: Pagination, doc_type: DocumentType, loc: list[str] = None
) -> tuple[dict[str, Any], SearchQuantity, str]:
    """
    Creates an ES sort based on the API's pagination model.

    Args:
        pagination: The API pagination setup.
        doc_type: The document type to target
        loc: Request location information for validation error messages
    """
    order_quantity, page_after_value = validate_pagination(pagination, doc_type, loc)

    sort: dict[str, Any] = {}
    if order_quantity.dynamic:
        path = order_quantity.get_dynamic_path()
        postfix = '.keyword'
        section = path[: -len(postfix)] if path.endswith(postfix) else path
        section = section.rsplit('.', 1)[0]
        sort = {
            path: {
                'order': pagination.order,
                'nested': {
                    'path': section,
                    'filter': order_quantity.get_dynamic_filter().to_dict(),
                },
            }
        }
    else:
        path = order_quantity.search_field
        sort = {order_quantity.search_field: pagination.order}

    # Add secondary sorting based on doc id
    if path != doc_type.id_field:
        sort[doc_type.id_field] = pagination.order

    return sort, order_quantity, page_after_value


def _api_to_es_aggregation(
    es_search: Search,
    name: str,
    agg: AggregationBase,
    doc_type: DocumentType,
    post_agg_query: models.Query,
    create_es_query: Callable[[models.Query], EsQuery],
) -> A:
    """
    Creates an ES aggregation based on the API's aggregation model.

    Args:
        name: Unique identifier for this aggregation.
        agg: The aggregation information
    """
    agg_name = f'agg:{name}'
    es_aggs = es_search.aggs
    filter = None

    # When the aggregation has been configured with exclude_from_search, we need
    # to remove any filters targeting the aggregated quantity in the aggregation
    # filters, but keep then in the post_agg_query
    if post_agg_query:
        if isinstance(agg, QuantityAggregation) and agg.exclude_from_search:
            filter = create_es_query(
                remove_quantity_from_query(post_agg_query, agg.quantity)
            )
        else:
            filter = create_es_query(post_agg_query)
    if filter is not None:
        es_aggs = es_aggs.bucket(f'{agg_name}:filtered', A('filter', filter=filter))

    if isinstance(agg, StatisticsAggregation):
        for metric_name in agg.metrics:
            metrics = doc_type.metrics
            if metric_name not in metrics and doc_type == material_type:
                metrics = material_entry_type.metrics
            if metric_name not in metrics:
                raise QueryValidationError(
                    'metric must be the qualified name of a suitable search quantity',
                    loc=['statistic', 'metrics'],
                )
            metric_aggregation, metric_quantity = metrics[metric_name]
            es_aggs.metric(
                f'statistics:{metric_name}',
                A(metric_aggregation, field=metric_quantity.qualified_field),
            )

        return

    # Get quantity aggregation details
    agg = cast(QuantityAggregation, agg)
    quantity = validate_quantity(
        agg.quantity, doc_type=doc_type, loc=['aggregation', 'quantity']
    )

    # When targeting nested fields, add nested aggregation
    longest_nested_key = None
    is_nested = False
    for nested_key in doc_type.nested_object_keys:
        if agg.quantity.startswith(nested_key):
            es_aggs = es_aggs.bucket(f'nested_agg:{name}', 'nested', path=nested_key)
            longest_nested_key = nested_key
            is_nested = True

    # If the quantity is dynamic, we need to add additional nested aggregation
    # filters that ensure the returned values target only the specified
    # quantity.
    if quantity.dynamic:
        es_aggs = es_aggs.bucket(
            f'nested_agg:{name}', 'nested', path='search_quantities'
        )
        is_nested = True
        longest_nested_key = 'search_quantities'
        es_aggs = es_aggs.bucket(
            f'nested_agg:{name}:filtered', A('filter', filter=quantity.dynamic_filter)
        )

    es_agg = None
    if isinstance(agg, TermsAggregation):
        if not quantity.annotation.aggregatable:
            raise QueryValidationError(
                'The aggregation quantity cannot be used in a terms aggregation.',
                loc=['aggregation', name, AggType.TERMS, 'quantity'],
            )

        if agg.pagination is not None:
            if post_agg_query is not None:
                raise QueryValidationError(
                    f'Aggregation pagination cannot be used with exclude_from_search in the same request',
                    loc=['aggregations', name, AggType.TERMS, 'pagination'],
                )

            if agg.size is not None:
                raise QueryValidationError(
                    f'You cannot paginate and provide an extra size parameter.',
                    loc=['aggregations', name, AggType.TERMS, 'pagination'],
                )

            order_quantity, page_after_value = validate_pagination(
                agg.pagination, doc_type=doc_type, loc=['aggregation']
            )

            # We are using elastic searchs 'composite aggregations' here. We do not really
            # compose aggregations, but only those pseudo composites allow us to use the
            # 'after' feature that allows to scan through all aggregation values.
            terms = A(
                AggType.TERMS, field=quantity.search_field, order=agg.pagination.order
            )

            if order_quantity is None:
                composite = {'sources': {name: terms}, 'size': agg.pagination.page_size}

            else:
                sort_terms = A(
                    AggType.TERMS,
                    field=order_quantity.search_field,
                    order=agg.pagination.order,
                )

                composite = {
                    'sources': [
                        {order_quantity.search_field: sort_terms},
                        {quantity.search_field: terms},
                    ],
                    'size': agg.pagination.page_size,
                }

            if page_after_value is not None:
                if order_quantity is None:
                    composite['after'] = {name: page_after_value}
                else:
                    try:
                        order_value, quantity_value = page_after_value.split(':')
                        composite['after'] = {
                            quantity.search_field: quantity_value,
                            order_quantity.search_field: order_value,
                        }
                    except Exception:
                        raise QueryValidationError(
                            f'The pager_after_value has not the right format.',
                            loc=[
                                'aggregations',
                                name,
                                'terms',
                                'pagination',
                                'page_after_value',
                            ],
                        )

            es_agg = es_aggs.bucket(agg_name, 'composite', **composite)

            # additional cardinality to get total
            es_aggs.metric(
                f'agg:{name}:total', 'cardinality', field=quantity.search_field
            )
        else:
            if agg.size is None:
                if quantity.default_aggregation_size is not None:
                    agg.size = quantity.default_aggregation_size

                elif quantity.values is not None:
                    agg.size = len(quantity.values)

                else:
                    agg.size = 10

            terms_kwargs: dict[str, Any] = {}
            if agg.include is not None:
                if isinstance(agg.include, str):
                    terms_kwargs['include'] = f'.*{agg.include}.*'
                else:
                    terms_kwargs['include'] = agg.include

            terms = A(
                AggType.TERMS,
                field=quantity.search_field,
                size=agg.size,
                **terms_kwargs,
            )
            es_agg = es_aggs.bucket(agg_name, terms)

        if agg.entries is not None and agg.entries.size > 0:
            kwargs: dict[str, Any] = {}
            if agg.entries.required is not None:
                if agg.entries.required.include is not None:
                    kwargs.update(_source=dict(includes=agg.entries.required.include))
                else:
                    kwargs.update(_source=dict(excludes=agg.entries.required.exclude))

            es_agg.metric('entries', A('top_hits', size=agg.entries.size, **kwargs))

        if is_nested:
            es_agg.bucket(f'agg:parents:{name}', A('reverse_nested'))

    elif isinstance(agg, AutoDateHistogramAggregation):
        if quantity.annotation.mapping['type'] not in ['date']:
            raise QueryValidationError(
                f'The quantity {quantity} cannot be used in a auto date histogram aggregation',
                loc=['aggregations', name, AggType.HISTOGRAM, 'quantity'],
            )

        es_agg = es_aggs.bucket(
            agg_name,
            A(
                AggType.AUTO_DATE_HISTOGRAM,
                field=quantity.search_field,
                buckets=agg.buckets,
                format='yyyy-MM-dd',
            ),
        )

    elif isinstance(agg, DateHistogramAggregation):
        if quantity.annotation.mapping['type'] not in ['date']:
            raise QueryValidationError(
                f'The quantity {quantity} cannot be used in a date histogram aggregation',
                loc=['aggregations', name, AggType.HISTOGRAM, 'quantity'],
            )

        es_agg = es_aggs.bucket(
            agg_name,
            A(
                AggType.DATE_HISTOGRAM,
                field=quantity.search_field,
                interval=agg.interval,
                format='yyyy-MM-dd',
            ),
        )

    elif isinstance(agg, HistogramAggregation):
        if quantity.annotation.mapping['type'] not in [
            'integer',
            'float',
            'double',
            'long',
            'date',
        ]:
            raise QueryValidationError(
                f'The quantity {quantity} cannot be used in a histogram aggregation',
                loc=['aggregations', name, AggType.HISTOGRAM, 'quantity'],
            )
        params: dict[str, Any] = {}
        if agg.offset is not None:
            params['offset'] = agg.offset
        if agg.extended_bounds is not None:
            params['extended_bounds'] = agg.extended_bounds.dict()
        es_agg = es_aggs.bucket(
            agg_name,
            A(
                AggType.HISTOGRAM,
                field=quantity.search_field,
                interval=agg.interval,
                **params,
            ),
        )

    elif isinstance(agg, MinMaxAggregation):
        if quantity.annotation.mapping['type'] not in [
            'integer',
            'float',
            'double',
            'long',
            'date',
        ]:
            raise QueryValidationError(
                f'The quantity {quantity} cannot be used in a mix-max aggregation',
                loc=['aggregations', name, 'min_max', 'quantity'],
            )

        es_aggs.metric(agg_name + ':min', A('min', field=quantity.search_field))
        es_aggs.metric(agg_name + ':max', A('max', field=quantity.search_field))

    else:
        raise NotImplementedError()

    if isinstance(agg, BucketAggregation):
        for metric_name in agg.metrics:
            metrics = doc_type.metrics
            if longest_nested_key == 'entries':
                metrics = material_entry_type.metrics
            if metric_name not in metrics:
                raise QueryValidationError(
                    'metric must be the qualified name of a suitable search quantity',
                    loc=['statistic', 'metrics'],
                )
            metric_aggregation, metric_quantity = metrics[metric_name]
            es_agg.metric(
                f'metric:{metric_name}',
                A(metric_aggregation, field=metric_quantity.qualified_field),
            )


def _es_to_api_aggregation(
    es_response,
    name: str,
    agg: AggregationBase,
    histogram_responses: dict[str, HistogramAggregation],
    bucket_values: dict[str, float],
    doc_type: DocumentType,
):
    """
    Creates a AggregationResponse from elasticsearch response on a request executed with
    the given aggregation.
    """
    es_aggs = es_response.aggs
    aggregation_dict = agg.dict(by_alias=True)
    filtered_agg_name = f'agg:{name}:filtered'
    if filtered_agg_name in es_response.aggs:
        es_aggs = es_aggs[f'agg:{name}:filtered']

    # The histogram config is returned using the original request.
    histogram_response = histogram_responses.get(name)
    bucket_value = bucket_values.get(name)
    if histogram_response is not None:
        aggregation_dict['buckets'] = histogram_response.buckets
        aggregation_dict['interval'] = histogram_response.interval

    # Statistics aggregation
    if isinstance(agg, StatisticsAggregation):
        metrics = {}
        for metric in agg.metrics:  # type: ignore
            metrics[metric] = es_aggs[f'statistics:{metric}'].value

        return AggregationResponse(
            statistics=StatisticsAggregationResponse(data=metrics, **aggregation_dict)
        )

    # If targeting nested object resolve nested aggregation result
    agg = cast(QuantityAggregation, agg)
    quantity = validate_quantity(agg.quantity, doc_type=doc_type)
    longest_nested_key = None
    for nested_key in doc_type.nested_object_keys:
        if agg.quantity.startswith(nested_key):
            es_aggs = es_aggs[f'nested_agg:{name}']
            longest_nested_key = nested_key

    # Dynamic quantity queries need to be translated back to using the original
    # name and response structure
    if quantity.dynamic:
        aggregation_dict['quantity'] = quantity.qualified_name
        es_aggs = es_aggs[f'nested_agg:{name}']
        es_aggs = es_aggs[f'nested_agg:{name}:filtered']
        longest_nested_key = 'search_quantities'

    # Resolves any type of bucket aggregation
    has_no_pagination = getattr(agg, 'pagination', None) is None
    if isinstance(agg, BucketAggregation):
        es_agg = es_aggs['agg:' + name]
        values: set = set()

        def get_bucket(es_bucket) -> Bucket:
            if has_no_pagination:
                if isinstance(agg, (DateHistogramAggregation)):
                    value = es_bucket['key_as_string']
                else:
                    value = es_bucket['key']
            elif agg.pagination.order_by is None:  # type: ignore
                value = es_bucket.key[name]
            else:
                value = es_bucket.key[quantity.search_field]

            nested_count = es_bucket.doc_count
            if f'agg:parents:{name}' in es_bucket:
                count = es_bucket[f'agg:parents:{name}'].doc_count
            else:
                count = nested_count
            metrics = {}
            for metric in agg.metrics:  # type: ignore
                metrics[metric] = es_bucket['metric:' + metric].value

            entries = None
            if 'entries' in es_bucket:
                if longest_nested_key:
                    entries = [
                        {longest_nested_key: item['_source'].to_dict()}
                        for item in es_bucket.entries.hits.hits
                    ]
                else:
                    entries = [
                        item['_source'].to_dict()
                        for item in es_bucket.entries.hits.hits
                    ]

            # By default ES returns values of 0 and 1 for terms aggregation
            # targeting boolean values. Here we transform them into True/False
            # to be more consistent.
            if (
                isinstance(agg, TermsAggregation)
                and quantity.annotation.mapping['type'] == 'boolean'
            ):
                if value == 0:
                    value = False
                elif value == 1:
                    value = True

            # Histograms for fields that contain only a single value have a
            # special response format where the single bucket contains the only
            # available value.
            if bucket_value is not None:
                value = bucket_value

            values.add(value)
            if len(metrics) == 0:
                metrics = None
            return Bucket(
                value=value,
                entries=entries,
                count=count,
                nested_count=nested_count,
                metrics=metrics,
            )

        data = [get_bucket(es_bucket) for es_bucket in es_agg.buckets]

        if has_no_pagination:
            # fill "empty" values
            if quantity.values is not None:
                for value in quantity.values:
                    if value not in values:
                        metrics = {metric: 0 for metric in agg.metrics}
                        if len(metrics) == 0:
                            metrics = None
                        data.append(Bucket(value=value, count=0, metrics=metrics))

        else:
            total = es_aggs[f'agg:{name}:total']['value']
            pagination = PaginationResponse(
                total=total, **aggregation_dict['pagination']
            )
            if (
                pagination.page_after_value is not None
                and pagination.page_after_value.endswith(':')
            ):
                pagination.page_after_value = pagination.page_after_value[0:-1]

            if 'after_key' in es_agg:
                after_key = es_agg['after_key']
                if pagination.order_by is None:
                    pagination.next_page_after_value = after_key[name]
                else:
                    str_values = [str(v) for v in after_key.to_dict().values()]
                    pagination.next_page_after_value = ':'.join(str_values)
            else:
                pagination.next_page_after_value = None

            aggregation_dict['pagination'] = pagination

        if isinstance(agg, TermsAggregation):
            return AggregationResponse(
                terms=TermsAggregationResponse(data=data, **aggregation_dict)
            )
        elif isinstance(agg, HistogramAggregation):
            return AggregationResponse(
                histogram=HistogramAggregationResponse(data=data, **aggregation_dict)
            )
        elif isinstance(agg, DateHistogramAggregation):
            return AggregationResponse(
                date_histogram=DateHistogramAggregationResponse(
                    data=data, **aggregation_dict
                )
            )
        elif isinstance(agg, AutoDateHistogramAggregation):
            return AggregationResponse(
                auto_date_histogram=AutoDateHistogramAggregationResponse(
                    data=data, interval=es_agg['interval'], **aggregation_dict
                )
            )
        else:
            raise NotImplementedError()

    if isinstance(agg, MinMaxAggregation):
        min_value = es_aggs[f'agg:{name}:min']['value']
        max_value = es_aggs[f'agg:{name}:max']['value']

        return AggregationResponse(
            min_max=MinMaxAggregationResponse(
                data=[min_value, max_value], **aggregation_dict
            )
        )

    raise NotImplementedError()


def _specific_agg(
    agg: Aggregation,
) -> (
    TermsAggregation
    | AutoDateHistogramAggregation
    | DateHistogramAggregation
    | HistogramAggregation
    | MinMaxAggregation
    | StatisticsAggregation
):
    if agg.terms is not None:
        return agg.terms

    if agg.histogram is not None:
        return agg.histogram

    if agg.date_histogram is not None:
        return agg.date_histogram

    if agg.auto_date_histogram is not None:
        return agg.auto_date_histogram

    if agg.min_max is not None:
        return agg.min_max

    if agg.statistics is not None:
        return agg.statistics

    raise NotImplementedError()


def _and_clauses(query: Query) -> Generator[Query, None, None]:
    if isinstance(query, models.And):
        for clause in query.op:
            yield from _and_clauses(clause)

    yield query


def _buckets_to_interval(
    owner: str = 'public',
    query: Query | EsQuery = None,
    aggregations: dict[str, Aggregation] = {},
    user_id: str = None,
    index: Index = entry_index,
) -> tuple[dict[str, Aggregation], dict[str, HistogramAggregation], dict[str, float]]:
    """Converts any histogram aggregations with the number of buckets into a
    query with an interval. This is required because elasticsearch does not yet
    support providing only the number of buckets.

    Buckets that have only one available value require a special treatment. An
    interval cannot be defined in such cases, so we use a dummy value of 1.
    """
    # Get the histograms which are determined by the number of buckets
    histogram_requests: dict[str, HistogramAggregation] = {}
    histogram_responses: dict[str, HistogramAggregation] = {}
    bucket_values: dict[str, float] = {}
    aggs = {name: _specific_agg(agg) for name, agg in aggregations.items()}
    for agg_name, agg in aggs.items():
        if isinstance(agg, HistogramAggregation):
            buckets = agg.buckets
            # When buckets have been defined, but no explicit limits are given,
            # a min-max aggregation has to be performed.
            if buckets is not None:
                histogram_requests[agg_name] = agg

    # If no buckets determined, continue normally
    if len(histogram_requests) == 0:
        return aggregations, histogram_responses, bucket_values

    # Create min/max aggregations for each histogram aggregation with buckets
    # only.
    min_max_aggregations = {
        agg_name: Aggregation(
            min_max=MinMaxAggregation(
                quantity=agg.quantity, exclude_from_search=agg.exclude_from_search
            )
        )
        for agg_name, agg in histogram_requests.items()
    }
    response = search(
        owner,
        query,
        MetadataPagination(page_size=0),
        None,
        min_max_aggregations,
        user_id,
        index,
    )

    # Calculate interval and return the modified aggregations
    for agg_name, agg in histogram_requests.items():
        data = response.aggregations[agg_name].min_max.data  # pylint: disable=no-member
        min_value = data[0]
        max_value = data[1]
        interval = None
        extended_bounds = agg.extended_bounds
        if agg.extended_bounds:
            if min_value is not None and extended_bounds.min is not None:
                min_value = min(min_value, extended_bounds.min)
            else:
                min_value = extended_bounds.min if min_value is None else min_value
            if max_value is not None and extended_bounds.max is not None:
                max_value = max(max_value, extended_bounds.max)
            else:
                max_value = extended_bounds.max if max_value is None else max_value
        if min_value is not None and max_value is not None:
            interval = (
                0
                if max_value == min_value
                else ((1 + 1e-8) * max_value - min_value) / agg.buckets
            )
            quantity = validate_quantity(agg.quantity, doc_type=index.doc_type)
            # Discretized fields require a 'ceiled' interval in order to not
            # return bins with floating point values and in order to prevent
            # binning inaccuracies
            if quantity.annotation.mapping['type'] in ['integer', 'long', 'date']:
                interval = math.ceil((max_value - min_value) / agg.buckets)
            # The interval for floating point fields is made artificially a bit
            # bigger. This prevents binning issues arising from floating point
            # inaccuracy.
            else:
                interval = (
                    0
                    if max_value == min_value
                    else ((1 + 1e-12) * max_value - min_value) / agg.buckets
                )

        # If no interval can be defined, the query interval is set to a dummy
        # value of 1. ES requires a non-empty value.
        response_interval = interval
        if not interval:
            interval = 1
            response_interval = None
            bucket_values[agg_name] = min_value
        histogram_responses[agg_name] = HistogramAggregation(
            quantity=agg.quantity,
            interval=response_interval,
            buckets=agg.buckets,
            offset=min_value,
        )
        aggregations[agg_name].histogram = agg.copy(
            update={'interval': interval, 'offset': min_value, 'buckets': None}
        )

    return aggregations, histogram_responses, bucket_values


def search(
    owner: str = 'public',
    query: Query | EsQuery = None,
    pagination: MetadataPagination = None,
    required: MetadataRequired = None,
    aggregations: dict[str, Aggregation] = {},
    user_id: str = None,
    index: Index = entry_index,
) -> MetadataResponse:
    # If histogram aggregations only provide the number of buckets, we need to
    # separately query the min/max values before forming the histogram
    # aggregation
    aggregations, histogram_responses, bucket_values = _buckets_to_interval(
        owner, query, aggregations, user_id, index
    )

    doc_type = index.doc_type
    skip_sort = False

    # The first half of this method creates the ES query. Then the query is run on ES.
    # The second half is about transforming the ES response to a MetadataResponse.

    # owner
    owner_query = _owner_es_query(owner=owner, user_id=user_id, doc_type=doc_type)

    # query
    if query is None:
        query = {}

    def create_es_query(query: Query):
        return _api_to_es_query(
            cast(Query, query), doc_type=doc_type, owner_query=owner_query
        )

    if isinstance(query, EsQuery):
        es_query = cast(EsQuery, query)
    else:
        # TODO this is a temporary performance hot-fix. Sort is expensive and we sort
        # by default. In the future, the client should explicitly state if sort is necessary.
        # Now, we simply do never sort, if there is a top-level AND match for a single id in the query.
        # In this case, there wil always be just one result and sorting is not necessary.
        # This catches a lot of problematic queries as a hot-fix.
        skip_sort = isinstance(query, dict) and isinstance(
            query.get(doc_type.id_field, None), str
        )
        query = normalize_api_query(cast(Query, query), doc_type=doc_type)
        es_query = create_es_query(cast(Query, query))

    nested_owner_query = owner_query
    if doc_type != entry_type:
        nested_owner_query = Q('nested', path='entries', query=owner_query)
    es_query &= nested_owner_query

    search = Search(index=index.index_name)

    # pagination
    if pagination is None:
        pagination = MetadataPagination()
    if pagination.order_by is None:
        pagination.order_by = doc_type.id_field

    sort, order_quantity, page_after_value = _api_to_es_sort(
        pagination, doc_type=doc_type
    )
    if not skip_sort:
        search = search.sort(sort)
    search = search.extra(size=pagination.page_size, track_total_hits=True)

    if pagination.page_offset:
        search = search.extra(**{'from': pagination.page_offset})
    elif pagination.page:
        search = search.extra(**{'from': (pagination.page - 1) * pagination.page_size})
    elif page_after_value:
        search = search.extra(search_after=page_after_value.rsplit(':', 1))

    # required
    includes, excludes, requires_filtering = _api_to_es_required(
        required, pagination, doc_type
    )
    search = search.source(includes=includes, excludes=excludes)  # pylint: disable=no-member

    # aggregations
    aggs = [(name, _specific_agg(agg)) for name, agg in aggregations.items()]
    excluded_agg_quantities = {
        agg.quantity
        for _, agg in aggs
        if isinstance(agg, QuantityAggregation) and agg.exclude_from_search
    }

    if len(excluded_agg_quantities) > 0:
        and_clauses = list(_and_clauses(query))
        pre_clauses = [
            and_clause
            for and_clause in and_clauses
            if isinstance(and_clause, models.Criteria)
            and and_clause.name not in excluded_agg_quantities
        ]

        pre_agg_es_query = _api_to_es_query(
            models.And(**{'and': list(pre_clauses)}),
            doc_type=doc_type,
            owner_query=owner_query,
        )
        post_agg_query = models.And(
            **{
                'and': [
                    and_clause
                    for and_clause in and_clauses
                    if and_clause not in pre_clauses
                ]
            }
        )
        post_agg_es_query = _api_to_es_query(
            post_agg_query, doc_type=doc_type, owner_query=owner_query
        )

        search = search.post_filter(post_agg_es_query)
        search = search.query(pre_agg_es_query & nested_owner_query)
    else:
        search = search.query(es_query)  # pylint: disable=no-member
        post_agg_query = None

    for name, agg in aggs:
        _api_to_es_aggregation(
            search,
            name,
            agg,
            doc_type=doc_type,
            post_agg_query=post_agg_query,
            create_es_query=create_es_query,
        )

    # execute
    try:
        es_response = search.execute()
    except RequestError as e:
        raise SearchError(e)
    more_response_data = {}

    # pagination
    pagination_response = _es_to_api_pagination(
        es_response, pagination, order_quantity, doc_type
    )

    # aggregations
    if len(aggregations) > 0:
        more_response_data['aggregations'] = cast(
            dict[str, Any],
            {
                name: _es_to_api_aggregation(
                    es_response,
                    name,
                    _specific_agg(agg),
                    histogram_responses,
                    bucket_values,
                    doc_type=doc_type,
                )
                for name, agg in aggregations.items()
            },
        )

    more_response_data['es_query'] = es_query.to_dict()
    if isinstance(query, EsQuery):
        # we cannot report EsQuery back, because it won't validate within the MetadataResponse model
        query = None

    # Precalculate the include/exclude patterns
    include_patterns = None
    exclude_patterns = None
    if required:
        include_patterns = (
            [pattern.split(schema_separator, 1)[0] for pattern in required.include]
            if required.include
            else None
        )
        exclude_patterns = (
            [pattern.split(schema_separator, 1)[0] for pattern in required.exclude]
            if required.exclude
            else None
        )

    result = MetadataResponse(
        owner='all' if owner is None else owner,
        query=query,
        pagination=pagination_response,
        required=required,
        data=[
            _es_to_entry_dict(
                hit, requires_filtering, include_patterns, exclude_patterns
            )
            for hit in es_response.hits
        ],
        **more_response_data,
    )

    return result


def search_iterator(
    owner: str = 'public',
    query: Query | EsQuery = None,
    order_by: str = 'entry_id',
    required: MetadataRequired = None,
    aggregations: dict[str, Aggregation] = {},
    user_id: str = None,
    index: Index = entry_index,
) -> Iterator[dict[str, Any]]:
    """
    Works like :func:`search`, but returns an iterator for iterating over the results.
    Consequently, you cannot specify `pagination`, only `order_buy`.
    """
    page_after_value = None
    while True:
        response = search(
            owner=owner,
            query=query,
            pagination=MetadataPagination(
                page_size=100, page_after_value=page_after_value, order_by=order_by
            ),
            required=required,
            aggregations=aggregations,
            user_id=user_id,
            index=index,
        )

        page_after_value = response.pagination.next_page_after_value

        yield from response.data

        if page_after_value is None or len(response.data) == 0:
            break


def quantity_values(
    quantity: str, page_size: int = 100, return_buckets: bool = False, **kwargs
) -> Generator[Any, None, None]:
    """
    A generator that uses ``search`` and an aggregation to retrieve all
    values of a quantity. Will run multiple requests with page_size until all values
    have been gathered. Kwargs are passed to search, e.g. to change owner or query.
    """
    page_after_value = None

    while True:
        aggregation = TermsAggregation(
            quantity=quantity,
            pagination=AggregationPagination(
                page_size=page_size, page_after_value=page_after_value
            ),
        )

        search_response = search(
            aggregations=dict(value_agg=Aggregation(terms=aggregation)),
            pagination=MetadataPagination(page_size=0),
            **kwargs,
        )

        value_agg = cast(
            TermsAggregationResponse, search_response.aggregations['value_agg'].terms
        )  # pylint: disable=no-member
        for bucket in value_agg.data:
            if return_buckets:
                yield bucket
            else:
                yield bucket.value

        if len(value_agg.data) < page_size:
            break

        page_after_value = value_agg.pagination.next_page_after_value
        if page_after_value is None:
            break
