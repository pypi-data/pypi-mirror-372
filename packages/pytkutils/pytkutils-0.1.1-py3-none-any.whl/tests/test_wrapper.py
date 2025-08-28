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

import pytest
import os
import shutil
import pytkutils
from pytkutils import wrapper


@pytest.fixture(scope="module")
def global_storage():
    return {
        "shape": "./tests/data/DK10f_A1tPnt5dLft.s",
        "shape_decompressed": "./tests/data/DK10f_A1tPnt5dLft_decompressed.s",
        "shape_compressed": "./tests/data/DK10f_A1tPnt5dLft_compressed.s",
        "worldfile": "./tests/data/w-005655+015119.w",
        "worldfile_decompressed": "./tests/data/w-005655+015119_decompressed.w",
        "worldfile_compressed": "./tests/data/w-005655+015119_compressed.w",
    }


@pytest.mark.dependency(name="test_shape_compression")
@pytest.mark.skipif(not os.path.exists("./TK.MSTS.Tokens.dll"), reason="requires TK.MSTS.Tokens.dll to be present in the file system")
def test_shape_compression(global_storage):
    shape_filepath = global_storage["shape"]
    shape_compressed_filepath = global_storage["shape_compressed"]

    result = wrapper.compress(shape_filepath, shape_compressed_filepath, "./TK.MSTS.Tokens.dll")
    
    assert result == True
    assert pytkutils.is_compressed(shape_compressed_filepath)


@pytest.mark.dependency(depends=["test_shape_compression"])
@pytest.mark.skipif(not os.path.exists("./TK.MSTS.Tokens.dll"), reason="requires TK.MSTS.Tokens.dll to be present in the file system")
def test_shape_decompression(global_storage):
    shape_compressed_filepath = global_storage["shape_compressed"]
    shape_decompressed_filepath = global_storage["shape_decompressed"]

    result = wrapper.decompress(shape_compressed_filepath, shape_decompressed_filepath, "./TK.MSTS.Tokens.dll")
    
    assert result == True
    assert not pytkutils.is_compressed(shape_decompressed_filepath)


@pytest.mark.dependency(name="test_worldfile_compression")
@pytest.mark.skipif(not os.path.exists("./TK.MSTS.Tokens.dll"), reason="requires TK.MSTS.Tokens.dll to be present in the file system")
def test_worldfile_compression(global_storage):
    worldfile_filepath = global_storage["worldfile"]
    worldfile_compressed_filepath = global_storage["worldfile_compressed"]

    result = wrapper.compress(worldfile_filepath, worldfile_compressed_filepath, "./TK.MSTS.Tokens.dll")
    
    assert result == True
    assert pytkutils.is_compressed(worldfile_compressed_filepath)


@pytest.mark.dependency(depends=["test_worldfile_compression"])
@pytest.mark.skipif(not os.path.exists("./TK.MSTS.Tokens.dll"), reason="requires TK.MSTS.Tokens.dll to be present in the file system")
def test_worldfile_decompression(global_storage):
    worldfile_compressed_filepath = global_storage["worldfile_compressed"]
    worldfile_decompressed_filepath = global_storage["worldfile_decompressed"]

    result = wrapper.decompress(worldfile_compressed_filepath, worldfile_decompressed_filepath, "./TK.MSTS.Tokens.dll")
    
    assert result == True
    assert not pytkutils.is_compressed(worldfile_decompressed_filepath)