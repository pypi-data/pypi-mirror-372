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

# DO NOT ANYMORE USE OR EXTEND THE SCHEMA.
# Only for purpose of compatibility. Use run schema plugin.
# https://github.com/nomad-coe/nomad-schema-plugin-run.git

import numpy as np  # noqa: F401

from nomad.datamodel.data import ArchiveSection
from nomad.datamodel.metainfo.common import FastAccess
from nomad.datamodel.metainfo.simulation.calculation import Calculation
from nomad.datamodel.metainfo.simulation.method import Method
from nomad.datamodel.metainfo.simulation.system import System
from nomad.metainfo import (  # noqa: F401
    Category,
    MCategory,
    MSection,
    Package,
    Quantity,
    Reference,
    Section,
    SectionProxy,
    SubSection,
)

m_package = Package()


class AccessoryInfo(MCategory):
    """
    Information that *in theory* should not affect the results of the calculations (e.g.,
    timing).
    """

    m_def = Category()


class ProgramInfo(MCategory):
    """
    Contains information on the program that generated the data, i.e. the program_name,
    program_version, program_compilation_host and program_compilation_datetime as direct
    children of this field.
    """

    m_def = Category(categories=[AccessoryInfo])


class Program(MSection):
    """
    Contains the specifications of the program.
    """

    m_def = Section(validate=False)

    name = Quantity(
        type=str,
        shape=[],
        description="""
        Specifies the name of the program that generated the data.
        """,
        categories=[AccessoryInfo, ProgramInfo],
    )

    version = Quantity(
        type=str,
        shape=[],
        description="""
        Specifies the official release version of the program that was used.
        """,
        categories=[AccessoryInfo, ProgramInfo],
    )

    version_internal = Quantity(
        type=str,
        description="""
        Specifies a program version tag used internally for development purposes.
        Any kind of tagging system is supported, including git commit hashes.
        """,
        categories=[ProgramInfo],
    )

    compilation_datetime = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='second',
        description="""
        Contains the program compilation date and time from *Unix epoch* (00:00:00 UTC on
        1 January 1970) in seconds. For date and times without a timezone, the default
        timezone GMT is used.
        """,
        categories=[AccessoryInfo, ProgramInfo],
    )

    compilation_host = Quantity(
        type=str,
        shape=[],
        description="""
        Specifies the host on which the program was compiled.
        """,
        categories=[AccessoryInfo, ProgramInfo],
    )


class TimeRun(MSection):
    """
    Contains information on timing information of the run.
    """

    m_def = Section(validate=False)

    date_end = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='second',
        description="""
        Stores the end date of the run as time since the *Unix epoch* (00:00:00 UTC on 1
        January 1970) in seconds. For date and times without a timezone, the default
        timezone GMT is used.
        """,
    )

    date_start = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='second',
        description="""
        Stores the start date of the run as time since the *Unix epoch* (00:00:00 UTC on 1
        January 1970) in seconds. For date and times without a timezone, the default
        timezone GMT is used.
        """,
    )

    cpu1_end = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='second',
        description="""
        Stores the end time of the run on CPU 1.
        """,
    )

    cpu1_start = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='second',
        description="""
        Stores the start time of the run on CPU 1.
        """,
    )

    wall_end = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='second',
        description="""
        Stores the internal wall-clock time at the end of the run.
        """,
    )

    wall_start = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        unit='second',
        description="""
        Stores the internal wall-clock time from the start of the run.
        """,
    )


class MessageRun(MSection):
    """
    Contains warning, error, and info messages of the run.
    """

    m_def = Section(validate=False)

    type = Quantity(
        type=str,
        shape=[],
        description="""
        Type of the message. Can be one of warning, error, info, debug.
        """,
    )

    value = Quantity(
        type=str,
        shape=[],
        description="""
        Value of the message of the computational program, given by type.
        """,
    )


class Run(ArchiveSection):
    """
    Every section run represents a single call of a program.
    """

    m_def = Section(validate=False)

    calculation_file_uri = Quantity(
        type=str,
        shape=[],
        description="""
        Contains the nomad uri of a raw the data file connected to the current run. There
        should be an value for the main_file_uri and all ancillary files.
        """,
    )

    clean_end = Quantity(
        type=bool,
        shape=[],
        description="""
        Indicates whether this run terminated properly (true), or if it was killed or
        exited with an error code unequal to zero (false).
        """,
    )

    raw_id = Quantity(
        type=str,
        shape=[],
        description="""
        An optional calculation id, if one is found in the code input/output files.
        """,
    )

    starting_run_ref = Quantity(
        type=Reference(SectionProxy('Run')),
        shape=[],
        description="""
        Links the current section run to a section run containing the calculations from
        which the current section starts.
        """,
        categories=[FastAccess],
    )

    n_references = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description="""
         Number of references to the current section calculation.
        """,
    )

    runs_ref = Quantity(
        type=Reference(SectionProxy('Run')),
        shape=['n_references'],
        description="""
        Links the the current section to other run sections. Such a link is necessary for
        example for workflows that may contain a series of runs.
        """,
        categories=[FastAccess],
    )

    program = SubSection(sub_section=Program.m_def)

    time_run = SubSection(sub_section=TimeRun.m_def)

    message = SubSection(sub_section=MessageRun.m_def)

    method = SubSection(sub_section=Method.m_def, repeats=True)

    system = SubSection(sub_section=System.m_def, repeats=True)

    calculation = SubSection(sub_section=Calculation.m_def, repeats=True)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)


m_package.__init_metainfo__()
