# -*- coding: utf-8 -*-
# constants.py
# Copyright (C) 2015-2017 LEAP
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
import platform

_system = platform.system()

IS_LINUX = _system == "Linux"
IS_MAC = _system == "Darwin"
IS_UNIX = IS_MAC or IS_LINUX
IS_WIN = _system == "Windows"

if IS_LINUX:
    BITMASK_ROOT_SYSTEM = '/usr/sbin/bitmask-root'
    BITMASK_ROOT_LOCAL = '/usr/local/sbin/bitmask-root'
    OPENVPN_SYSTEM = '/usr/sbin/openvpn'
    OPENVPN_LOCAL = '/usr/local/sbin/leap-openvpn'
    POLKIT_LOCAL = '/usr/share/polkit-1/actions/se.leap.bitmask-bundle.policy'
    POLKIT_SYSTEM = '/usr/share/polkit-1/actions/se.leap.bitmask.policy'
