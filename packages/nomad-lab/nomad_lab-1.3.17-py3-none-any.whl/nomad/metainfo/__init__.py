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
The NOMAD meta-info allows to define schemas for physics data independent of the used
storage format. It allows to define physics quantities with types, complex shapes
(vectors, matrices, etc.), units, links, and descriptions. It allows to organize large
amounts of these quantities in containment hierarchies of extendable sections, references
between sections, and additional quantity categories.

NOMAD uses the meta-info to define all archive data, repository meta-data, (and encyclopedia
data). The meta-info provides a convenient Python interface to create,
manipulate, and access data. We also use it to map data to various storage formats,
including JSON, mongodb, and elastic search.
"""

from .metainfo import (
    MSectionBound,
    MSection,
    MCategory,
    Definition,
    Attribute,
    Property,
    Quantity,
    SubSection,
    Section,
    Category,
    Package,
    SchemaPackage,
    MEnum,
    Datetime,
    Capitalized,
    MProxy,
    MetainfoError,
    DeriveError,
    MetainfoReferenceError,
    Reference,
    SectionReference,
    QuantityReference,
    File,
    URL,
    Datetime,
    Unit,
    JSON,
    Dimension,
    Bytes,
    Context,
    m_package,
    SectionProxy,
    derived,
    constraint,
    units,
)
from .annotation import (
    Annotation,
    DefinitionAnnotation,
    SectionAnnotation,
    AnnotationModel,
)
from .data_type import (
    Datatype,
    Primitive,
    Number,
    ExactNumber,
    InexactNumber,
    NonPrimitive,
    URL,
    File,
    Any,
    Capitalized,
    Bytes,
    JSON,
    Dimension,
    Unit,
    Callable,
    Datetime,
    Enum,
)
