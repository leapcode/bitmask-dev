# -*- coding: utf-8 -*-
# linux
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
Linux VPN launcher implementation.
"""

import commands
import os

from twisted.logger import Logger

from leap.bitmask.util import STANDALONE
from leap.bitmask.vpn.utils import first, force_eval
from leap.bitmask.vpn.privilege import LinuxPolicyChecker
from leap.bitmask.vpn.launcher import VPNLauncher

logger = Logger()
COM = commands


class LinuxVPNLauncher(VPNLauncher):

    # The following classes depend on force_eval to be called against
    # the classes, to get the evaluation of the standalone flag on runtine.
    # If we keep extending this kind of classes, we should abstract the
    # handling of the STANDALONE flag in a base class

    class BITMASK_ROOT(object):
        def __call__(self):
            _global = '/usr/sbin/bitmask-root'
            _local = '/usr/local/sbin/bitmask-root'
            if os.path.isfile(_global):
                return _global
            elif os.path.isfile(_local):
                return _local
            else:
                return 'bitmask-root'

    class OPENVPN_BIN_PATH(object):
        def __call__(self):
            return ("/usr/local/sbin/leap-openvpn" if STANDALONE else
                    "/usr/sbin/openvpn")

    class POLKIT_PATH(object):
        def __call__(self):
            # LinuxPolicyChecker will give us the right path if standalone.
            return LinuxPolicyChecker.get_polkit_path()

    OTHER_FILES = (POLKIT_PATH, BITMASK_ROOT, OPENVPN_BIN_PATH)

    @classmethod
    def get_vpn_command(kls, vpnconfig, providerconfig, socket_host,
                        remotes, socket_port="unix", openvpn_verb=1):
        """
        Returns the Linux implementation for the vpn launching command.

        Might raise:
            NoPkexecAvailable,
            NoPolkitAuthAgentAvailable,
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
        # we use `super` in order to send the class to use
        command = super(LinuxVPNLauncher, kls).get_vpn_command(
            vpnconfig, providerconfig, socket_host, socket_port, remotes,
            openvpn_verb)

        command.insert(0, force_eval(kls.BITMASK_ROOT))
        command.insert(1, "openvpn")
        command.insert(2, "start")

        policyChecker = LinuxPolicyChecker()
        pkexec = policyChecker.maybe_pkexec()
        if pkexec:
            command.insert(0, first(pkexec))

        return command

    @classmethod
    def cmd_for_missing_scripts(kls, frompath):
        """
        Returns a sh script that can copy the missing files.

        :param frompath: The path where the helper files live
        :type frompath: str

        :rtype: str
        """
        bin_paths = force_eval(
            (LinuxVPNLauncher.POLKIT_PATH,
             LinuxVPNLauncher.OPENVPN_BIN_PATH,
             LinuxVPNLauncher.BITMASK_ROOT))

        polkit_path, openvpn_bin_path, bitmask_root = bin_paths

        # no system config for now
        # sys_config = kls.SYSTEM_CONFIG
        (polkit_file, openvpn_bin_file,
         bitmask_root_file) = map(
            lambda p: os.path.split(p)[-1],
            bin_paths)

        cmd = '#!/bin/sh\n'
        cmd += 'mkdir -p /usr/local/sbin\n'

        cmd += 'cp "%s" "%s"\n' % (os.path.join(frompath, polkit_file),
                                   polkit_path)
        cmd += 'chmod 644 "%s"\n' % (polkit_path, )

        cmd += 'cp "%s" "%s"\n' % (os.path.join(frompath, bitmask_root_file),
                                   bitmask_root)
        cmd += 'chmod 744 "%s"\n' % (bitmask_root, )

        if flags_STANDALONE:
            cmd += 'cp "%s" "%s"\n' % (
                os.path.join(frompath, openvpn_bin_file),
                openvpn_bin_path)
            cmd += 'chmod 744 "%s"\n' % (openvpn_bin_path, )

        return cmd
