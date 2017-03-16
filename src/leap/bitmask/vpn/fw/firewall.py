# -*- coding: utf-8 -*-
# manager.py
# Copyright (C) 2015 LEAP
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
# alng with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Firewall Manager
"""

import commands
import subprocess

from leap.bitmask.vpn.constants import IS_MAC
from leap.common.events import catalog, emit_async


class FirewallManager(object):

    """
    Firewall manager that blocks/unblocks all the internet traffic with some
    exceptions.
    This allows us to achieve fail close on a vpn connection.
    """

    # FIXME -- get the path
    BITMASK_ROOT = "/usr/local/sbin/bitmask-root"

    def __init__(self, remotes):
        """
        Initialize the firewall manager with a set of remotes that we won't
        block.

        :param remotes: the gateway(s) that we will allow
        :type remotes: list
        """
        self._remotes = remotes

    def start(self, restart=False):
        """
        Launch the firewall using the privileged wrapper.

        :returns: True if the exitcode of calling the root helper in a
                  subprocess is 0.
        :rtype: bool
        """
        gateways = [gateway for gateway, port in self._remotes]

        # XXX check for wrapper existence, check it's root owned etc.
        # XXX check that the iptables rules are in place.

        cmd = ["pkexec", self.BITMASK_ROOT, "firewall", "start"]
        if restart:
            cmd.append("restart")

        # FIXME -- use a processprotocol
        exitCode = subprocess.call(cmd + gateways)
        emit_async(catalog.VPN_STATUS_CHANGED)

        if exitCode == 0:
            return True
        else:
            return False

    # def tear_down_firewall(self):
    def stop(self):
        """
        Tear the firewall down using the privileged wrapper.
        """
        if IS_MAC:
            # We don't support Mac so far
            return True

        exitCode = subprocess.call(["pkexec", self.BITMASK_ROOT,
                                    "firewall", "stop"])
        emit_async(catalog.VPN_STATUS_CHANGED)
        if exitCode == 0:
            return True
        else:
            return False

    def is_up(self):
        """
        Return whether the firewall is up or not.

        :rtype: bool
        """
        # TODO test this, refactored from is_fw_down

        cmd = "pkexec {0} firewall isup".format(self.BITMASK_ROOT)
        output = commands.getstatusoutput(cmd)[0]

        return output != 256

    @property
    def status(self):
        status = 'off'
        if self.is_up():
            status = 'on'

        return {'status': status, 'error': None}
