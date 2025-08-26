# Copyright 2018 Markus Scheidgen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an"AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import bz2
import gzip
import lzma
import os
import tarfile
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import contextmanager
from typing import IO, Any

import pint

from nomad.datamodel import EntryArchive
from nomad.metainfo import MSection, SubSection
from nomad.utils import get_logger


class FileParser(ABC):
    """
    Base class for file parsers. The parse method specific to a file type
    should be implemented in the corresponding child class. The parsed quantities are
    stored in results. One can access a quantity by using the get method or as attribute.

    Arguments:
        mainfile: the path to the file to be parsed
        logger: optional logger
        open: function to open file
    """

    def __init__(self, mainfile: str | IO = None, logger=None, open: Callable = None):
        self._mainfile: str = None
        self._mainfile_obj: IO = None
        if isinstance(mainfile, str):
            self._mainfile = os.path.abspath(mainfile)
            self._mainfile_obj = None
        elif hasattr(mainfile, 'name'):
            self._mainfile = mainfile.name
            self._mainfile_obj = mainfile
        self._open: Callable = open
        self.logger = logger if logger is not None else get_logger(__name__)
        # a key is necessary for xml parsers, where parsing is done dynamically
        self._key: str = None
        self._kwargs: dict[str, Any] = {}
        self._results: dict[str, Any] = None
        self._file_handler: Any = None

    def reset(self):
        """
        Nullifies the parsed results.
        """
        self._results = None
        self._file_handler = None

    @property
    def results(self):
        """
        Returns the parsed results.
        """
        if self._results is None:
            self._results = dict()
        if self._key not in self._results:
            self.parse(self._key, **self._kwargs)

        return self._results

    @property
    def maindir(self):
        """
        Returns the directory where the mainfile is located.
        """
        return os.path.dirname(self._mainfile)

    @property
    def mainfile_obj(self):
        """
        Returns the mainfile object.
        """
        if self._mainfile_obj is None:
            try:
                self._mainfile_obj = self.open(self._mainfile)
            except Exception:
                pass

        return self._mainfile_obj

    @contextmanager
    def open_mainfile_obj(self):
        """
        Returns the mainfile object with a context.
        """
        try:
            self._mainfile_obj = self.open(self._mainfile)
            yield self._mainfile_obj
        except Exception:
            pass
        finally:
            if self._mainfile_obj is not None:
                self._mainfile_obj.close()
                self._mainfile_obj = None

    @property
    def mainfile(self):
        """
        Returns the path to the mainfile.
        """
        if self._mainfile is None:
            return

        if self._mainfile_obj is None and not os.path.isfile(self._mainfile):
            return
        return self._mainfile

    @mainfile.setter
    def mainfile(self, val):
        """
        Assigns the mainfile to be parsed.
        """
        self.reset()
        self._mainfile = None
        if isinstance(val, str):
            self._mainfile = os.path.abspath(val)
            self._mainfile_obj = None
        elif hasattr(val, 'name'):
            self._mainfile = val.name
            self._mainfile_obj = val

    def open(self, mainfile: str):
        """
        Opens the file with the provided open function or based on the file type.
        """
        open_file = self._open
        if open_file is None:
            if mainfile.endswith('.gz'):
                open_file = gzip.open
            elif mainfile.endswith('.bz2'):
                open_file = bz2.open
            elif mainfile.endswith('.xz'):
                open_file = lzma.open
            elif mainfile.endswith('.tar'):
                open_file = tarfile.open
            else:
                open_file = open

        try:
            return open_file(mainfile)
        except Exception:
            pass

    def get(
        self,
        key: str,
        default: Any = None,
        unit: pint.Unit | pint.Quantity = None,
        **kwargs,
    ):
        """
        Returns the parsed result for quantity with name key. If quantity is not in
        results default will be returned. A pint unit can be provided which is attached
        to the returned value.
        """
        if self.mainfile is None:
            return default

        self._key = key
        self._kwargs = kwargs
        val = self.results.get(key)
        if val is None:
            val = default

        if val is None:
            return

        if unit is not None:
            if isinstance(unit, pint.Quantity | pint.Unit):
                val = val * unit

            elif isinstance(val, pint.Quantity):
                val = val.to(unit)

            else:
                val = pint.Quantity(val, unit)

        return val

    def to_dict(self):
        """
        Recursively converts the the parser results into a dictionary.
        """
        results = {}
        for key, val in self.results.items():
            if isinstance(val, FileParser):
                val = val.to_dict()
            elif isinstance(val, list) and val and isinstance(val[0], FileParser):
                for n, val_n in enumerate(val):
                    val[n] = val_n.to_dict()

            results[key] = val
        return results

    def write_to_archive(self, section: MSection):
        """
        Wrapper for the m_from_dict functionality of msection to write the parser
        results to an archive section.
        """
        return section.m_from_dict(self.to_dict())

    @abstractmethod
    def parse(self, quantity_key: str = None, **kwargs):
        pass

    def pop(self, key, default=None):
        return self._results.pop(key, default)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.get(key)
        elif isinstance(key, int):
            return self[int]

    def __setitem__(self, key, val):
        if self._results is None:
            self._results = {}
        self._results[key] = val

    def __getattr__(self, key):
        if self._results is None:
            self._results = {}
            self.parse(key)
        return self._results.get(key)

    def __repr__(self) -> str:
        results = list(self._results.keys()) if self._results else []
        string = f'{self.__class__.__name__}'
        if self.mainfile:
            string += f'({os.path.basename(self.mainfile)}) '
        if results:
            string += f'--> {len(results)} parsed quantities ({", ".join(results[:5])}{", ..." if len(results) > 5 else ""})'
        return string

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._mainfile_obj:
            self._mainfile_obj.close()
        if self._file_handler is not None:
            try:
                self._file_handler.close()
            except Exception:
                pass


class ArchiveWriter(ABC):
    mainfile: str = None
    archive: EntryArchive = None
    logger = None
    child_archives: dict[str, EntryArchive] = None

    def get_mainfile_keys(self, filename: str, decoded_buffer: str) -> bool | list[str]:
        """
        If child archives are necessary for the entry, a list of keys for the archives are
        returned.
        """
        return True

    # TODO replace with MSection.m_update_from_dict once it takes in type Quantity?
    def parse_section(self, data: dict[str, Any], root: MSection) -> None:
        """
        Write the quantities in data into an archive section.
        """
        for key, val in data.items():
            if not hasattr(root, key):
                continue

            section = getattr(root.m_def.section_cls, key)
            if isinstance(section, SubSection):
                for val_n in [val] if isinstance(val, dict) else val:
                    sub_section = section.sub_section.section_cls()
                    root.m_add_sub_section(section, sub_section)
                    self.parse_section(val_n, sub_section)
                continue

            root.m_set(root.m_get_quantity_definition(key), val)

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the parsed metadata into a dictionary following the nomad archive schema.
        """
        return {}

    def write_to_archive(self) -> None:
        """
        Abstract method to write the parsed metadata from mainfile to archive. The parser
        may directly write to the archive or convert to a dictionary following the archive
        schema through the to_dict method which is then used to update the archive.
        """
        if self.archive is None:
            return

        self.archive.m_update_from_dict(self.to_dict())

    def write(
        self, mainfile: str, archive: EntryArchive, logger=None, child_archives=None
    ) -> None:
        """
        Wrapper to write_to_archive method.
        """
        self.mainfile = mainfile
        self.archive = archive
        self.logger = logger if logger else get_logger(__name__)
        self.child_archives = child_archives

        self.write_to_archive()

    def parse(
        self, mainfile: str, archive: EntryArchive, logger=None, child_archives=None
    ) -> None:
        """
        Wraps write method for backwards compatibility.
        """
        self.write(mainfile, archive, logger, child_archives)
