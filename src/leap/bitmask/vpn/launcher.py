# -*- coding: utf-8 -*-
# launcher.py
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
Platform-independent VPN launcher interface.
"""

import getpass
import os
import stat

from twisted.logger import Logger

from abc import ABCMeta, abstractmethod

from leap.bitmask.vpn.constants import IS_MAC
from leap.bitmask.vpn.utils import force_eval


log = Logger()


flags_STANDALONE = False


class VPNLauncherException(Exception):
    pass


class OpenVPNNotFoundException(VPNLauncherException):
    pass


def _has_updown_scripts(path, warn=True):
    """
    Checks the existence of the up/down scripts and its
    exec bit if applicable.

    :param path: the path to be checked
    :type path: str

    :param warn: whether we should log the absence
    :type warn: bool

    :rtype: bool
    """
    is_file = os.path.isfile(path)
    if warn and not is_file:
        log.error('Could not find up/down script %s. '
                  'Might produce DNS leaks.' % (path,))

    # XXX check if applies in win
    is_exe = False
    try:
        is_exe = (stat.S_IXUSR & os.stat(path)[stat.ST_MODE] != 0)
    except OSError as e:
        log.warn("%s" % (e,))
    if warn and not is_exe:
        log.error('Up/down script %s is not executable. '
                  'Might produce DNS leaks.' % (path,))
    return is_file and is_exe


def _has_other_files(path, warn=True):
    """
    Check the existence of other important files.

    :param path: the path to be checked
    :type path: str

    :param warn: whether we should log the absence
    :type warn: bool

    :rtype: bool
    """
    is_file = os.path.isfile(path)
    if warn and not is_file:
        log.warn('Could not find file during checks: %s. ' % (
                 path,))
    return is_file


class VPNLauncher(object):
    """
    Abstract launcher class
    """
    __metaclass__ = ABCMeta

    UPDOWN_FILES = None
    OTHER_FILES = None
    UP_SCRIPT = None
    DOWN_SCRIPT = None

    PREFERRED_PORTS = ("443", "80", "53", "1194")

    @classmethod
    @abstractmethod
    def get_vpn_command(kls, vpnconfig, providerconfig,
                        socket_host, socket_port, remotes, openvpn_verb=1):
        """
        Return the platform-dependant vpn command for launching openvpn.

        Might raise:
            OpenVPNNotFoundException,
            VPNLauncherException.

        :param vpnconfig: vpn configuration object
        :type vpnconfig: VPNConfig
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
        openvpn_path = force_eval(kls.OPENVPN_BIN_PATH)

        if not os.path.isfile(openvpn_path):
            log.warn('Could not find openvpn bin in path %s' % (
                     openvpn_path))
            err = OpenVPNNotFoundException()
            err.expected = True
            raise err

        args = []

        args += [
            '--nobind'
        ]

        if openvpn_verb is not None:
            args += ['--verb', '%d' % (openvpn_verb,)]

        gateways = remotes

        for ip, port in gateways:
            args += ['--remote', ip, port, 'udp']

        args += [
            '--client',
            '--tls-client',
            '--remote-cert-tls',
            'server',
        ]

        openvpn_configuration = vpnconfig.get_openvpn_configuration()
        for key, value in openvpn_configuration.items():
            if type(value) is bool:
                if value:
                    args += ['--%s' % (key,)]
            else:
                args += ['--%s' % (key,), value]

        user = getpass.getuser()

        if socket_port == "unix":  # that's always the case for linux
            args += [
                '--management-client-user', user
            ]

        args += [
            '--management-signal',
            '--management', socket_host, socket_port,
            '--ca', providerconfig.get_ca_cert_path(),
            '--cert', vpnconfig.get_client_cert_path(providerconfig),
            '--key', vpnconfig.get_client_cert_path(providerconfig)
        ]

        command_and_args = [openvpn_path] + args
        return command_and_args
