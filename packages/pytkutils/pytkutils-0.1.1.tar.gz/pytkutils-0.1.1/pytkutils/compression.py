"""
This file is part of pyTKUtils.

Copyright (C) 2025 Peter Grønbæk Andersen <peter@grnbk.io>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import os
import shutil
import codecs
import tempfile
from typing import Optional

from . import wrapper


def is_compressed(filepath: str) -> Optional[bool]:
    """
    Determines whether a file is compressed.

    Args:
        filepath (str): Path to the file to inspect.

    Returns:
        bool:
            - True if the file appears to be compressed (binary format).
            - False if the file appears to be uncompressed (text format with a known header).
            - None if the file is readable as text but does not match known headers.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        OSError: If an I/O error occurs while opening the file.
    """
    with open(filepath, "rb") as f:
        bom = f.read(2)
        is_unicode = (bom == b"\xFF\xFE")

        if is_unicode:
            buffer = f.read(32)
            header = buffer.decode("utf-16le")[:16]
        else:
            buffer = bom + f.read(14)
            header = buffer.decode("ascii", errors="ignore")[:8]

        if header.startswith("SIMISA@F") or header.startswith("\r\nSIMISA@F"):
            return True

        elif header.startswith("SIMISA@@") or header.startswith("\r\nSIMISA@@"):
            return False

        return None


def compress(
    tkutils_dll_filepath: str,
    input_filepath: str,
    output_filepath: Optional[str] = None
) -> bool:
    """
    Compresses a file if it is not already compressed.

    If `output_filepath` is None, the file is compressed in place using a temporary file.
    If the file is already compressed, no changes are made. If an output path is given
    and the file is already compressed, it is simply copied to the destination.

    Args:
        tkutils_dll_filepath (str): Path to the TK.MSTS.Tokens DLL.
        input_filepath (str): Path to the input file.
        output_filepath (Optional[str]): Destination path for the compressed file,
                                         or None to compress in place.

    Returns:
        bool: True if compression was performed, False if the file was already compressed
              and was either copied or left unchanged.

    Raises:
        EnvironmentError: If required runtime dependencies (Mono or .NET) are missing.
        FileNotFoundError: If the input file or specified DLL file is not found.
        ImportError: If the DLL fails to load.
        OSError: If file operations fail.
    """
    already_compressed = is_compressed(input_filepath)

    if output_filepath is None:
        if already_compressed:
            return False
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_filepath = tmp.name
        
        try:
            wrapper.compress(input_filepath, tmp_filepath, tkutils_dll_filepath)
            os.replace(tmp_filepath, input_filepath)
            return True
        finally:
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)
    else:
        if already_compressed:
            if input_filepath != output_filepath:
                shutil.copyfile(input_filepath, output_filepath)
            
            return False
        
        return wrapper.compress(input_filepath, output_filepath, tkutils_dll_filepath)


def decompress(
    tkutils_dll_filepath: str,
    input_filepath: str,
    output_filepath: Optional[str] = None
) -> bool:
    """
    Decompresses a file if it is currently compressed.

    If `output_filepath` is None, the file is decompressed in place using a temporary file.
    If the file is already decompressed, no changes are made. If an output path is given
    and the file is already decompressed, it is simply copied to the destination.

    Args:
        tkutils_dll_filepath (str): Path to the TK.MSTS.Tokens DLL.
        input_filepath (str): Path to the input file.
        output_filepath (Optional[str]): Destination path for the decompressed file,
                                         or None to decompress in place.

    Returns:
        bool: True if decompression was performed, False if the file was already decompressed
              and was either copied or left unchanged.

    Raises:
        EnvironmentError: If required runtime dependencies (Mono or .NET) are missing.
        FileNotFoundError: If the input file or specified DLL file is not found.
        ImportError: If the DLL fails to load.
        OSError: If file operations fail.
    """
    currently_compressed = is_compressed(input_filepath)

    if output_filepath is None:
        if not currently_compressed:
            return False
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_filepath = tmp.name
        
        try:
            wrapper.decompress(input_filepath, tmp_filepath, tkutils_dll_filepath)
            os.replace(tmp_filepath, input_filepath)
            return True
        finally:
            if os.path.exists(tmp_filepath):
                os.remove(tmp_filepath)
        
    else:
        if not currently_compressed:
            if input_filepath != output_filepath:
                shutil.copyfile(input_filepath, output_filepath)
            
            return False
        
        return wrapper.decompress(input_filepath, output_filepath, tkutils_dll_filepath)

