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

"""This module contains common functions that do not depend on any of the NOMAD
source code. Notably, this module should be importable anywhere in the NOMAD
source code without circular imports.
"""

import os
import pkgutil
import shutil
import tarfile
import zipfile
from tempfile import TemporaryDirectory
from typing import Literal

import httpx


def get_package_path(package_name: str) -> str:
    """Given a python package name, returns the filepath of the package root folder.

    Raises:
        ValueError: If the given package cannot be loaded.
    """
    package_path = None
    try:
        # We try to deduce the package path from the top-level package
        package_path_segments = package_name.split('.')
        root_package = package_path_segments[0]
        package_dirs = package_path_segments[1:]
        package_path = os.path.join(
            os.path.dirname(
                pkgutil.get_loader(root_package).get_filename()  # type: ignore
            ),
            *package_dirs,
        )
        if not os.path.isdir(package_path):
            # We could not find it this way. Let's try to official way
            package_path = os.path.dirname(
                pkgutil.get_loader(package_name).get_filename()  # type: ignore
            )
    except Exception as e:
        raise ValueError(f'The python package {package_name} cannot be loaded.', e)

    return package_path


def download_file(url: str, filepath: str) -> str | None:
    """Used to download a file from the given URL to the given directory.

    Arg:
        url: URL pointing to a file to download.
        filepath: Path where the file is download into. If points to an existing
            directory, the file is saved there. Otherwise, creates a new file in
            that exact filepath.
    Returns:
        str: The path to the downloaded file.

    Raises:
        ValueError: If the given file cannot be downloaded.
    """
    if os.path.isdir(filepath):
        filename = url.rsplit('/')[-1]
        final_filepath = os.path.join(filepath, filename)
    else:
        filename = os.path.basename(filepath)
        final_filepath = filepath
    directory = os.path.dirname(final_filepath)

    try:
        with httpx.stream(
            'GET',
            url,
        ) as response:
            response.raise_for_status()
            # Download into a temporary directory to ensure the integrity of
            # the download
            with TemporaryDirectory() as tmp_folder:
                tmp_filepath = os.path.join(tmp_folder, filename)
                with open(tmp_filepath, mode='wb') as file:
                    for chunk in response.iter_bytes(chunk_size=10 * 1024):
                        file.write(chunk)
                # If download has succeeeded, copy the files over to
                # final location
                os.makedirs(directory, exist_ok=True)
                shutil.copyfile(tmp_filepath, final_filepath)
    except Exception as e:
        raise ValueError(f'Could not fetch file from URL: {url}') from e

    return final_filepath


decompress_file_extensions = {
    '.zip': 'zip',
    '.tgz': 'tar',
    '.gz': 'tar',
    '.tar.gz': 'tar',
    '.tar.bz2': 'tar',
    '.tar': 'tar',
    '.eln': 'zip',
}


def get_compression_format(path: str) -> Literal['zip', 'tar', 'error'] | None:
    """
    Returns the decompression format ('zip', 'tar' or 'error') if `path` specifies a file
    which should be automatically decompressed before adding it to an upload. If `path`
    does *not* specify a file which we think should be decompressed, or if it specifies a
    directory, we return None.

    The value 'error' means that we think this file should be decompressed, but that we cannot
    decompress it. This indicates that the file is corrupted, has a bad file format, or has
    the wrong file extension.

    Note, some files, like for example excel files, are actually zip files, and we don't want
    to extract such files. Therefore, we only auto decompress if the file has an extension
    we recognize as decompressable, like ".zip", ".tar" etc.
    """
    if os.path.isdir(path):
        return None
    basename_lower = os.path.basename(path).lower()
    for extension, format in decompress_file_extensions.items():
        if basename_lower.endswith(extension):
            if format == 'tar':
                return 'tar' if tarfile.is_tarfile(path) else 'error'
            elif format == 'zip':
                return 'zip' if zipfile.is_zipfile(path) else 'error'
    return None


def extract_file(
    filepath: str,
    directory: str = None,
    format: Literal['zip', 'tar', 'error'] = None,
    remove_archive: bool = True,
):
    """Extracts the given file in place. Supports extracting .zip and .tar
    files.

    Arg:
        filepath: Path of the file to extract.
        format: File format. The format will be guessed if not given.
        directory: Directory where to extract files. If not given, defaults to
            the directory where the archive file is.
        remove_archive: Whether to remove the archive files after successful
            extraction.

    Raises:
        ValueError: If the given file could not be extracted.
    """
    format = format or get_compression_format(filepath)
    directory = directory or os.path.dirname(filepath)
    if format:
        try:
            if format == 'zip':
                with zipfile.ZipFile(filepath) as zf:
                    zf.extractall(directory)
            elif format == 'tar':
                with tarfile.open(filepath) as tf:
                    tf.extractall(directory)
            elif format == 'error':
                raise ValueError('Could not open file.')
        except Exception as e:
            raise ValueError(
                'Cannot extract file. Bad file format or file extension?'
            ) from e
        else:
            if remove_archive:
                os.remove(filepath)


def is_url(path) -> bool:
    """Utility function for determining whether a filepath represents a URL."""
    return path.startswith('http://') or path.startswith('https://')


def is_safe_basename(basename: str) -> bool:
    """
    Checks if `basename` is a *safe* base name (file/folder name). We consider it safe if
    it is not empty, does not contain any '/', and is not equal to '.' or '..'
    """
    if not basename or '/' in basename or basename == '.' or basename == '..':
        return False
    return True


def is_safe_path(path: str, safe_path: str, is_directory=True) -> bool:
    """Returns whether the given path ultimately points to a known safe
    location. Can be used to prevent path traversal attacks, such as relative
    paths or symlinks.

        Args:
            path: The path to check
            safe_path: A safe location. Can be a folder or a file.
            is_directory: Whether the safe path is a directory or not. If True,
                a trailing slash is added and only the common prefix is tested.
                If False, the whole path must match. Otherwise users may access
                other locations with the same name prefix (e.g. /safe2 when
                safe_path was /safe).
    """
    real_path = os.path.realpath(path)
    if is_directory:
        if not safe_path.endswith(os.path.sep):
            safe_path += os.path.sep
        return os.path.commonprefix((real_path, safe_path)) == safe_path

    return real_path == safe_path


def is_safe_relative_path(path: str) -> bool:
    """
    Checks if path is a *safe* relative path. We consider it safe if it does not start with
    '/' or use '.' or '..' elements (which could be open for security leaks if allowed).
    It may end with a single '/', indicating that a folder is referred. For referring to
    the base folder, the empty string should be used (not '.' etc).
    """
    if not isinstance(path, str):
        return False
    if path == '':
        return True
    if path.startswith('/') or '//' in path or '\n' in path:
        return False

    depth = 0
    for element in path.split(os.sep):
        if element == '.':
            continue
        if element == '..':
            depth -= 1
        else:
            depth += 1
        # If depth at any point goes negative, it means the path goes outside
        # the base folder
        if depth < 0:
            return False

    return True
