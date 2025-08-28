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
import tempfile
import pytest
import pytkutils.compression as pytkutils


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "test.s"
    f.write_text("SIMISA@@\nThis is uncompressed text")
    return str(f)


@pytest.fixture
def dll_file(tmp_path):
    f = tmp_path / "TK.MSTS.Tokens.dll"
    f.write_text("dummy dll")
    return str(f)


def test_compress_already_compressed_with_output(monkeypatch, sample_file, dll_file, tmp_path):
    monkeypatch.setattr(pytkutils, "is_compressed", lambda path: True)

    called = {}
    monkeypatch.setattr(pytkutils.wrapper, "compress", lambda inp, out, dll: called.setdefault("compress", True))

    out = tmp_path / "out.s"
    result = pytkutils.compress(dll_file, sample_file, str(out))
    assert result is False
    assert "compress" not in called
    assert os.path.exists(out)  # should just copy


def test_compress_already_compressed_inplace(monkeypatch, sample_file, dll_file):
    monkeypatch.setattr(pytkutils, "is_compressed", lambda path: True)

    called = {}
    monkeypatch.setattr(pytkutils.wrapper, "compress", lambda inp, out, dll: called.setdefault("compress", True))

    result = pytkutils.compress(dll_file, sample_file, None)
    assert result is False
    assert "compress" not in called


def test_compress_not_compressed_with_output(monkeypatch, sample_file, dll_file, tmp_path):
    monkeypatch.setattr(pytkutils, "is_compressed", lambda path: False)

    called = {}

    def fake_compress(inp, out, dll):
        called["compress"] = True
        shutil.copyfile(inp, out)
        return True

    monkeypatch.setattr(pytkutils.wrapper, "compress", fake_compress)

    out = tmp_path / "out.s"
    result = pytkutils.compress(dll_file, sample_file, str(out))
    assert result is True
    assert "compress" in called
    assert os.path.exists(out)


def test_compress_not_compressed_inplace(monkeypatch, sample_file, dll_file):
    monkeypatch.setattr(pytkutils, "is_compressed", lambda path: False)

    called = {}

    def fake_compress(inp, out, dll):
        called["compress"] = True
        shutil.copyfile(inp, out)
        return True

    monkeypatch.setattr(pytkutils.wrapper, "compress", fake_compress)

    result = pytkutils.compress(dll_file, sample_file, None)
    assert result is True
    assert "compress" in called


def test_decompress_already_decompressed_with_output(monkeypatch, sample_file, dll_file, tmp_path):
    monkeypatch.setattr(pytkutils, "is_compressed", lambda path: False)

    called = {}
    monkeypatch.setattr(pytkutils.wrapper, "decompress", lambda inp, out, dll: called.setdefault("decompress", True))

    out = tmp_path / "out.s"
    result = pytkutils.decompress(dll_file, sample_file, str(out))
    assert result is False
    assert "decompress" not in called
    assert os.path.exists(out)  # should just copy


def test_decompress_not_decompressed_inplace(monkeypatch, sample_file, dll_file):
    monkeypatch.setattr(pytkutils, "is_compressed", lambda path: True)

    called = {}

    def fake_decompress(inp, out, dll):
        called["decompress"] = True
        shutil.copyfile(inp, out)
        return True

    monkeypatch.setattr(pytkutils.wrapper, "decompress", fake_decompress)

    result = pytkutils.decompress(dll_file, sample_file, None)
    assert result is True
    assert "decompress" in called

