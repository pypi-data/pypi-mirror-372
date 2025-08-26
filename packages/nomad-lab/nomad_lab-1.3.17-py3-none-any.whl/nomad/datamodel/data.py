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

import os.path
from typing import Any

from cachetools import TTLCache, cached
from pydantic import Field

from nomad.config import config
from nomad.metainfo.elasticsearch_extension import Elasticsearch, material_entry_type
from nomad.metainfo.metainfo import (
    JSON,
    Capitalized,
    Category,
    Datetime,
    MCategory,
    MSection,
    Quantity,
    Reference,
    Section,
)
from nomad.metainfo.pydantic_extension import PydanticModel


class ArchiveSection(MSection):
    """
    Base class for sections in a NOMAD archive. Provides a framework for custom
    section normalization via the `normalize` function.
    """

    normalizer_level = 0

    def normalize(self, archive, logger):
        """
        Is called during entry normalization. If you overwrite this with custom
        normalization code, make sure to call `super(YourClass, self).normalize(archive, logger)`.
        Otherwise, not all normalize functions might be called for section definitions
        with multiple base-classes.

        Arguments:
            archive: The whole archive that is normalized.
            logger: The structlog logger used during normalization.
        """
        pass


class EntryDataCategory(MCategory):
    pass


class ElnIntegrationCategory(EntryDataCategory):
    m_def = Category(
        label='Third-party ELN Integration', categories=[EntryDataCategory]
    )


class BasicElnCategory(EntryDataCategory):
    m_def = Category(label='Basic ELN', categories=[EntryDataCategory])


class ElnExampleCategory(EntryDataCategory):
    m_def = Category(label='Example ELNs', categories=[EntryDataCategory])


class UseCaseElnCategory(EntryDataCategory):
    m_def = Category(label='Use-cases', categories=[EntryDataCategory])


class WorkflowsElnCategory(EntryDataCategory):
    m_def = Category(label='Workflows', categories=[EntryDataCategory])


class EntryData(ArchiveSection):
    """
    An empty base section definition. This can be used to add new top-level sections
    to an entry.
    """

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        from nomad.datamodel import EntryArchive
        from nomad.datamodel.results import Results

        # TODO entry_type should only be assigned if not already defined (done to pass eln test)
        if archive.metadata:
            if not archive.metadata.entry_type and isinstance(
                self.m_parent, EntryArchive
            ):
                archive.metadata.entry_type = self.m_def.name
            if archive.metadata.entry_name is None and archive.metadata.mainfile:
                archive.metadata.entry_name = os.path.basename(
                    archive.metadata.mainfile
                )

        if not archive.results:
            archive.results = Results()


class Author(MSection):
    """A person that is author of data in NOMAD or references by NOMAD."""

    name = Quantity(
        type=str,
        derived=lambda user: f'{user.first_name} {user.last_name}'.strip(),
        a_elasticsearch=[
            Elasticsearch(material_entry_type, _es_field='keyword'),
            Elasticsearch(
                material_entry_type, mapping='text', field='text', _es_field=''
            ),
            Elasticsearch(suggestion='default'),
        ],
    )

    first_name = Quantity(type=Capitalized)
    last_name = Quantity(type=Capitalized)
    email = Quantity(type=str)

    affiliation = Quantity(type=str)
    affiliation_address = Quantity(type=str)


class User(Author):
    """A NOMAD user.

    Typically a NOMAD user has a NOMAD account. The user related data is managed by
    NOMAD keycloak user-management system. Users are used to denote authors,
    reviewers, and owners of datasets.

    Args:
        user_id: The unique, persistent keycloak UUID
        username: The unique, persistent, user chosen username
        first_name: The users first name (including all other given names)
        last_name: The users last name
        affiliation: The name of the company and institutes the user identifies with
        affiliation_address: The address of the given affiliation
        created: The time the account was created
        repo_user_id: The id that was used to identify this user in the NOMAD CoE Repository
        is_admin: Bool that indicated, if the user is the admin
    """

    m_def = Section(a_pydantic=PydanticModel())

    user_id = Quantity(type=str, a_elasticsearch=Elasticsearch(material_entry_type))

    username = Quantity(type=str)

    created = Quantity(type=Datetime)

    repo_user_id = Quantity(
        type=str,
        description='Optional, legacy user id from the old NOMAD CoE repository.',
    )

    is_admin = Quantity(
        type=bool, derived=lambda user: user.user_id == config.services.admin_user_id
    )

    is_oasis_admin = Quantity(type=bool, default=False)

    @staticmethod
    @cached(TTLCache(maxsize=2048, ttl=24 * 3600))
    def get(*args, **kwargs) -> 'User':
        from nomad import infrastructure

        return infrastructure.user_management.get_user(*args, **kwargs)  # type: ignore

    def full_user(self) -> 'User':
        """Returns a User object with all attributes loaded from the user management system."""
        from nomad import infrastructure

        assert self.user_id is not None
        return infrastructure.user_management.get_user(user_id=self.user_id)  # type: ignore


class UserReference(Reference):
    def __init__(self):
        super().__init__(User.m_def)

    def serialize_self(self, section):
        return {'type_kind': 'User', 'type_data': 'User'}

    def _normalize_impl(self, section, value):
        if isinstance(value, User):
            return value

        if isinstance(value, str):
            try:
                return User.get(value)
            except Exception as _exc:  # noqa
                return value

        raise ValueError(f'Cannot normalize {value}.')

    def _serialize_impl(self, section, value):
        if isinstance(value, str):
            return value
        if isinstance(value, User):
            return value.user_id

        raise ValueError(f'Cannot serialize {value}.')


class AuthorReference(Reference):
    def __init__(self):
        super().__init__(Author.m_def)

    def serialize_self(self, section):
        return {'type_kind': 'Author', 'type_data': 'Author'}

    def _normalize_impl(self, section, value):
        if isinstance(value, Author):
            return value

        if isinstance(value, dict):
            return Author.m_from_dict(value)

        if isinstance(value, str):
            try:
                return User.get(value)
            except Exception as _exc:  # noqa
                return value

        raise ValueError(f'Cannot normalize {value}.')

    def _serialize_impl(self, section, value):
        if isinstance(value, str):
            return value
        if isinstance(value, User):
            return value.user_id
        if isinstance(value, Author):
            return value.m_to_dict()

        raise ValueError(f'Cannot serialize {value}.')


class Query(JSON):
    """
    To represent a search query, including the applied filters and the results.

    filters : dict
        A dictionary of filters applied to the search. Keys are filter names, and values are the filter values.
    query : MetadataResponse
        A dictionary of the used query in the current search.
    """

    def _normalize_impl(self, value, **kwargs):
        from nomad.app.v1.models import MetadataResponse

        class QueryResult(MetadataResponse):
            filters: dict[str, Any] | None = Field(None)

        return QueryResult.model_validate(value).model_dump(by_alias=True)


Schema = EntryData
