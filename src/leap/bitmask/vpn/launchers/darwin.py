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

import getpass
import os
import socket
import sys

from twisted.logger import Logger

from leap.bitmask.vpn.launcher import VPNLauncher
from leap.bitmask.vpn.launcher import VPNLauncherException
from leap.common.config import get_path_prefix


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
        # TODO check cmd is in allowed list
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


class NoTunKextLoaded(VPNLauncherException):
    pass


class DarwinVPNLauncher(VPNLauncher):
    """
    VPN launcher for the Darwin Platform
    """
    UP_SCRIPT = None
    DOWN_SCRIPT = None

    # TODO -- move this to bitmask-helper

    # Hardcode the installation path for OSX for security, openvpn is
    # run as root
    INSTALL_PATH = "/Applications/Bitmask.app/"
    INSTALL_PATH_ESCAPED = os.path.realpath(os.getcwd() + "/../../")
    OPENVPN_BIN = 'openvpn.leap'
    OPENVPN_PATH = "%s/Contents/Resources/openvpn" % (INSTALL_PATH,)
    OPENVPN_PATH_ESCAPED = "%s/Contents/Resources/openvpn" % (
        INSTALL_PATH_ESCAPED,)
    OPENVPN_BIN_PATH = "%s/Contents/Resources/%s" % (INSTALL_PATH,
                                                     OPENVPN_BIN)
    if not os.path.isfile(OPENVPN_BIN_PATH):
        # let's try with the homebrew path
        OPENVPN_BIN_PATH = '/usr/local/sbin/openvpn'
    OTHER_FILES = []

    @classmethod
    def is_kext_loaded(kls):
        # latest versions do not need tuntap, so we're going to deprecate
        # the kext checking.
        True

    @classmethod
    def get_vpn_command(kls, vpnconfig, providerconfig, socket_host,
                        remotes, socket_port="unix", openvpn_verb=1):
        """
        Returns the OSX implementation for the vpn launching command.

        Might raise:
            NoTunKextLoaded,
            OpenVPNNotFoundException,
            VPNLauncherException.

        :param eipconfig: eip configuration object
        :type eipconfig: EIPConfig
        :param providerconfig: provider specific configuration
        :type providerconfig: ProviderConfig
        :param socket_host: either socket path (unix) or socket IP
        :type socket_host: str
        :param socket_port: either string "unix" if it's a unix socket,
                            or port otherwise
        :type socket_port: str
        :param openvpn_verb: the openvpn verbosity wanted
        :type openvpn_verb: int

        :return: A VPN command ready to be launched.
        :rtype: list
        """
        # if not kls.is_kext_loaded():
        #    raise NoTunKextLoaded('tun kext is needed, but was not found')

        # we use `super` in order to send the class to use
        command = super(DarwinVPNLauncher, kls).get_vpn_command(
            vpnconfig, providerconfig, socket_host, socket_port, remotes,
            openvpn_verb)
        command.extend(['--setenv', "LEAPUSER", getpass.getuser()])

        return command

    # TODO ship statically linked binary and deprecate.
    @classmethod
    def get_vpn_env(kls):
        """
        Returns a dictionary with the custom env for the platform.
        This is mainly used for setting LD_LIBRARY_PATH to the correct
        path when distributing a standalone client

        :rtype: dict
        """
        ld_library_path = os.path.join(get_path_prefix(), "..", "lib")
        ld_library_path.encode(sys.getfilesystemencoding())
        return {
            "DYLD_LIBRARY_PATH": ld_library_path
        }
