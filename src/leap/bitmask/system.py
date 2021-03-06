# -*- coding: utf-8 -*-
# platform.py
# Copyright (C) 2018 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
System constants
"""
import os
import platform

_system = platform.system()

IS_LINUX = _system == "Linux"
IS_MAC = _system == "Darwin"
IS_UNIX = IS_MAC or IS_LINUX
IS_WIN = _system == "Windows"
IS_SNAP = os.environ.get('SNAP')
