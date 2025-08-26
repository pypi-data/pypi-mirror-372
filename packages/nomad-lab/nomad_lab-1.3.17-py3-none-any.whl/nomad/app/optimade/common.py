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

from typing import cast

from nomad.metainfo.data_type import Datatype, to_optimade_type
from nomad.metainfo.elasticsearch_extension import SearchQuantity, entry_type
from nomad.metainfo.metainfo import Quantity, Reference

_provider_specific_fields: dict[str, SearchQuantity] = None


def create_provider_field(name, definition):
    if not definition.is_scalar:
        optimade_type = 'list'
    elif isinstance(definition.type, Datatype):
        optimade_type = to_optimade_type(definition.type)
    else:
        raise NotImplementedError(
            f'Optimade provider field with NOMAD type {definition.type} not implemented.'
        )

    description = definition.description
    if not description:
        description = 'no description available'

    return dict(name=name, description=description, type=optimade_type, sortable=False)


def provider_specific_fields() -> dict[str, SearchQuantity]:
    global _provider_specific_fields

    if _provider_specific_fields is not None:
        return _provider_specific_fields

    _provider_specific_fields = {}

    if len(entry_type.quantities) == 0:
        # TODO this is necessary, because the mappings are only created after the
        # ES index with initialized in infrastructure. But this is called during
        # optimade import. Detangle mapping creation from index creation!
        from nomad.datamodel.datamodel import EntryArchive

        entry_type.create_mapping(EntryArchive.m_def)

    for qualified_name, search_quantity in entry_type.quantities.items():
        quantity = cast(Quantity, search_quantity.definition)
        if isinstance(quantity.type, Reference):
            # we can't yet support those
            continue

        nmd_name = qualified_name
        nmd_name_split = nmd_name.split('.')

        if len(nmd_name_split) == 1:
            # plain metadata
            pass
        elif nmd_name_split[0] not in ['results']:
            # other domains fields that do not make sense in the optimade context
            continue
        elif len(nmd_name_split) > 2 and nmd_name_split[1] == 'optimade':
            # these are already in optimade
            continue

        opt_name = nmd_name.replace('.', '_')
        _provider_specific_fields[opt_name] = search_quantity

    return _provider_specific_fields
