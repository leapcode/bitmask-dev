# -*- coding: utf-8 -*-
# darwin.py
# Copyright (C) 2013-2017 LEAP
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
Darwin VPN launcher implementation.
"""

import os
import socket

from twisted.logger import Logger

from leap.bitmask.vpn.launcher import VPNLauncher
from leap.bitmask.vpn.launcher import VPNLauncherException


logger = Logger()


class HelperCommand(object):

    SOCKET_ADDR = '/tmp/bitmask-helper.socket'

    def __init__(self):
        pass

    def _connect(self):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self._sock.connect(self.SOCKET_ADDR)
        except socket.error, msg:
            raise RuntimeError(msg)

    def send(self, cmd, args=''):
        self._connect()
        sock = self._sock
        data = ""

        command = cmd + ' ' + args + '/CMD'

        try:
            sock.sendall(command)
            while '\n' not in data:
                data += sock.recv(32)
        finally:
            sock.close()

        return data


class DarwinVPNLauncher(VPNLauncher):
    """
    VPN launcher for the Darwin Platform
    """
    UP_SCRIPT = None
    DOWN_SCRIPT = None

    # TODO -- move this to bitmask-helper??

    # Hardcode the installation path for OSX for security, openvpn is
    # run as root
    INSTALL_PATH = "/Applications/Bitmask.app/"
    INSTALL_PATH_ESCAPED = os.path.realpath(os.getcwd() + "/../../")
    OPENVPN_BIN = 'openvpn.leap'
    OPENVPN_PATH = "%s/Contents/Resources/openvpn" % (INSTALL_PATH,)
    OPENVPN_PATH_ESCAPED = "%s/Contents/Resources/openvpn" % (
        INSTALL_PATH_ESCAPED,)
    OTHER_FILES = []

    _openvpn_bin_path = "%s/Contents/Resources/%s" % (
        INSTALL_PATH, OPENVPN_BIN)
    if os.path.isfile(_openvpn_bin_path):
        OPENVPN_BIN_PATH = _openvpn_bin_path
    else:
        # let's try with the homebrew path
        OPENVPN_BIN_PATH = '/usr/local/sbin/openvpn'

    def kill_previous_openvpn():
        pass
