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
Parser for creating artificial test, brenchmark, and demonstration data.
"""

import json
import os
import os.path
import random
import re
import signal
import sys
import time

import numpy
from ase.data import chemical_symbols

from nomad.datamodel import EntryArchive
from nomad.datamodel.metainfo import runschema

from .parser import MatchingParser, Parser


class EmptyParser(MatchingParser):
    """
    Implementation that produces an empty code_run
    """

    def parse(
        self, mainfile: str, archive: EntryArchive, logger=None, child_archives=None
    ) -> None:
        run = runschema.run.Run()
        archive.run.append(run)
        run.program = runschema.run.Program(name=self.code_name)


class TemplateParser(Parser):
    """
    A parser that generates data based on a template given via the
    mainfile. The template is basically some archive json. Only
    """

    name = 'parsers/template'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.code_name = 'Template'

    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ) -> bool:
        return filename.endswith('template.json')

    def parse(
        self, mainfile: str, archive: EntryArchive, logger=None, child_archives=None
    ) -> None:
        # tell tests about received logger
        if logger is not None:
            logger.debug('received logger')

        template_json = json.load(open(mainfile))
        loaded_archive = EntryArchive.m_from_dict(template_json)
        archive.m_add_sub_section(EntryArchive.run, loaded_archive.run[0])
        archive.m_add_sub_section(EntryArchive.workflow2, loaded_archive.workflow2)

        if 'warning' in mainfile:
            logger.warn('a test warning.')

        logger.debug('a test log entry')


class ChaosParser(Parser):
    """
    Parser that emulates typical error situations. Files can contain a json string (or
    object with key `chaos`) with one of the following string values:
    - exit
    - deadlock
    - consume_ram
    - exception
    - segfault
    - random
    """

    name = 'parsers/chaos'

    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ) -> bool:
        return filename.endswith('chaos.json')

    def parse(
        self, mainfile: str, archive: EntryArchive, logger=None, child_archives=None
    ) -> None:
        chaos_json = json.load(open(mainfile))
        if isinstance(chaos_json, str):
            chaos = chaos_json
        elif isinstance(chaos_json, dict):
            chaos = chaos_json.get('chaos', None)
        else:
            chaos = None

        if chaos == 'random':
            chaos = random.choice(
                ['exit', 'deadlock', 'consume_ram', 'exception', 'segfault']
            )

        if chaos == 'exit':
            sys.exit(1)
        elif chaos == 'deadlock':
            while True:
                time.sleep(1)
        elif chaos == 'consume_ram':
            data = []
            i = 0
            while True:
                data.append('a' * 10**6)
                i += 1
                logger.info(f'ate {i} mb')
        elif chaos == 'exception':
            raise Exception('Some chaos happened, muhuha...')
        elif chaos == 'segfault':
            os.kill(os.getpid(), signal.SIGSEGV)

        raise Exception('Unknown chaos')


class GenerateRandomParser(TemplateParser):
    name = 'parsers/random'

    basis_set_types = [
        'Numeric AOs',
        'Gaussians',
        '(L)APW+lo',
        'Plane waves',
        'Real-space grid',
        'Local-orbital minimum-basis',
    ]

    electronic_structure_methods = [
        'DFT',
        'DFT+U',
        'full-CI',
        'CIS',
        'CISDCCS',
        'CCS(D)',
        'CCSD',
        'CCSD(T)',
        'CCSDT(Q)',
        'MP2',
        'MP3',
        'MP4',
        'MP5',
        'MP6',
        'G0W0',
        'scGW',
        'LDA',
        'hybrid',
        'CASPT2',
        'MRCIS',
        'MRCISD',
        'RAS-CI',
    ]

    XC_functional_names = [
        'LDA_X',
        'LDA_C',
        'GGA_X',
        'GGA_C',
        'HYB_GGA_XC',
        'MGGA_X',
        'MGGA_C',
        'HYB_MGGA_XC',
    ]

    low_numbers = [1, 1, 2, 2, 2, 2, 2, 3, 3, 4]

    def is_mainfile(
        self,
        filename: str,
        mime: str,
        buffer: bytes,
        decoded_buffer: str,
        compression: str = None,
    ) -> bool:
        return re.match(r'.*?random_\d+', filename) is not None

    def parse(
        self, mainfile: str, archive: EntryArchive, logger=None, child_archives=None
    ) -> None:
        file_dir = os.path.dirname(os.path.abspath(__file__))
        relative_template_file = 'random_template.json'
        template_file = os.path.normpath(os.path.join(file_dir, relative_template_file))

        super().parse(template_file, archive, logger)

        seed = int(os.path.basename(mainfile).split('_')[1])
        random.seed(seed)
        numpy.random.seed(seed)

        run = archive.run[0]

        if not runschema:
            return

        for system in run.system:
            atoms = []
            atom_positions = []
            # different atoms
            for _ in range(0, random.choice(GenerateRandomParser.low_numbers)):
                # ase data starts with a place holder value X, we don't want that
                atom = random.choice(chemical_symbols[1:])
                # atoms of the same number
                for _ in range(0, random.choice(GenerateRandomParser.low_numbers)):
                    atoms.append(atom)
                    atom_positions.append([0.0, 0.0, 0.0])

            system.atoms = runschema.system.Atoms(
                labels=atoms, positions=atom_positions
            )

        run.program_basis_set_type = random.choice(GenerateRandomParser.basis_set_types)

        for method in run.method:
            method.electronic = runschema.method.Electronic(
                method=random.choice(GenerateRandomParser.electronic_structure_methods)
            )
            method.dft = runschema.method.DFT(
                xc_functional=runschema.method.XCFunctional(
                    name=random.choice(GenerateRandomParser.XC_functional_names)
                )
            )
