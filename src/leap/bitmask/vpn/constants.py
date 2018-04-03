# -*- coding: utf-8 -*-
# constants.py
# Copyright (C) 2015-2018 LEAP
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
from leap.bitmask.system import IS_LINUX

if IS_LINUX:
    BITMASK_ROOT_SYSTEM = '/usr/sbin/bitmask-root'
    BITMASK_ROOT_LOCAL = '/usr/local/sbin/bitmask-root'
    # this should change when bitmask is also a snap. for now,
    # snap is only RiseupVPN
    BITMASK_ROOT_SNAP = '/snap/bin/riseup-vpn.bitmask-root'

    OPENVPN_SYSTEM = '/usr/sbin/openvpn'
    OPENVPN_LOCAL = '/usr/local/sbin/leap-openvpn'
    # this should change when bitmask is also a snap. for now,
    # snap is only RiseupVPN
    OPENVPN_SNAP = '/snap/bin/riseup-vpn.openvpn'
    POLKIT_LOCAL = '/usr/share/polkit-1/actions/se.leap.bitmask.bundle.policy'
    POLKIT_SYSTEM = '/usr/share/polkit-1/actions/se.leap.bitmask.policy'
    POLKIT_SNAP = ('/usr/share/polkit-1/actions/'
                   'se.leap.bitmask.riseupvpn.policy')
