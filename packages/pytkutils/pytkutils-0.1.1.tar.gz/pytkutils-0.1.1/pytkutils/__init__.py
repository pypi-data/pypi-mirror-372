"""
pyTKUtils

A Python wrapper for the TK.MSTS.Tokens.dll library by Okrasa Ghia.

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

__version__ = '0.1.1'
__all__ = [
    'is_compressed', 'compress', 'decompress',
]

__author__ = 'Peter Grønbæk Andersen <peter@grnbk.io>'

from .compression import is_compressed, compress, decompress
