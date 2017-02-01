# -*- coding: utf-8 -*-
# process.py
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
VPN Process management.
A custom processProtocol launches the VPNProcess and connects to its management
interface.
"""

import os
import shutil
import socket
import subprocess
import sys

from itertools import chain, repeat

from twisted.internet import defer, protocol, reactor
from twisted.internet import error as internet_error
from twisted.internet.task import LoopingCall
from twisted.logger import Logger

from leap.bitmask.vpn.constants import IS_MAC
from leap.bitmask.vpn.utils import first, force_eval
from leap.bitmask.vpn.utils import get_vpn_launcher
from leap.bitmask.vpn.launchers import linux
from leap.bitmask.vpn.udstelnet import UDSTelnet
from leap.bitmask.vpn import _observer
from leap.bitmask.vpn import _management

logger = Logger()


# OpenVPN verbosity level - from flags.py
OPENVPN_VERBOSITY = 1


class VPNProcess(protocol.ProcessProtocol, _management.VPNManagement):
    """
    A ProcessProtocol class that can be used to spawn a process that will
    launch openvpn and connect to its management interface to control it
    programmatically.
    """

    def __init__(self, eipconfig, providerconfig, socket_host, socket_port,
                 signaler, openvpn_verb, remotes):
        """
        :param eipconfig: eip configuration object
        :type eipconfig: EIPConfig

        :param providerconfig: provider specific configuration
        :type providerconfig: ProviderConfig

        :param socket_host: either socket path (unix) or socket IP
        :type socket_host: str

        :param socket_port: either string "unix" if it's a unix
                            socket, or port otherwise
        :type socket_port: str

        :param signaler: Signaler object used to receive notifications to the
                         backend
        :type signaler: backend.Signaler

        :param openvpn_verb: the desired level of verbosity in the
                             openvpn invocation
        :type openvpn_verb: int
        """
        _management.VPNManagement.__init__(self, signaler=signaler)

        self._eipconfig = eipconfig
        self._providerconfig = providerconfig
        self._socket_host = socket_host
        self._socket_port = socket_port

        self._launcher = get_vpn_launcher()

        self._last_state = None
        self._last_status = None
        self._alive = False

        # XXX use flags, maybe, instead of passing
        # the parameter around.
        self._openvpn_verb = openvpn_verb

        self._vpn_observer = _observer.VPNObserver(signaler)
        self.is_restart = False

        self._remotes = remotes

    # processProtocol methods

    def connectionMade(self):
        """
        Called when the connection is made.

        .. seeAlso: `http://twistedmatrix.com/documents/13.0.0/api/twisted.internet.protocol.ProcessProtocol.html` # noqa
        """
        self._alive = True
        self.aborted = False
        self.try_to_connect_to_management(max_retries=10)

    def outReceived(self, data):
        """
        Called when new data is available on stdout.

        :param data: the data read on stdout

        .. seeAlso: `http://twistedmatrix.com/documents/13.0.0/api/twisted.internet.protocol.ProcessProtocol.html` # noqa
        """
        # truncate the newline
        line = data[:-1]
        logger.info(line)
        self._vpn_observer.watch(line)

    def processExited(self, reason):
        """
        Called when the child process exits.

        .. seeAlso: `http://twistedmatrix.com/documents/13.0.0/api/twisted.internet.protocol.ProcessProtocol.html` # noqa
        """
        exit_code = reason.value.exitCode
        if isinstance(exit_code, int):
            logger.debug("processExited, status %d" % (exit_code,))
        if self._signaler is not None:
            self._signaler.signal(
                self._signaler.eip_process_finished, exit_code)
        self._alive = False

    def processEnded(self, reason):
        """
        Called when the child process exits and all file descriptors associated
        with it have been closed.

        .. seeAlso: `http://twistedmatrix.com/documents/13.0.0/api/twisted.internet.protocol.ProcessProtocol.html` # noqa
        """
        exit_code = reason.value.exitCode
        if isinstance(exit_code, int):
            logger.debug("processEnded, status %d" % (exit_code,))

    # polling

    def pollStatus(self):
        """
        Polls connection status.
        """
        if self._alive:
            self.get_status()

    def pollState(self):
        """
        Polls connection state.
        """
        if self._alive:
            self.get_state()

    # launcher

    def getCommand(self):
        """
        Gets the vpn command from the aproppriate launcher.

        Might throw:
            VPNLauncherException,
            OpenVPNNotFoundException.

        :rtype: list of str
        """
        command = self._launcher.get_vpn_command(
            eipconfig=self._eipconfig,
            providerconfig=self._providerconfig,
            socket_host=self._socket_host,
            socket_port=self._socket_port,
            openvpn_verb=self._openvpn_verb,
            remotes=self._remotes)

        encoding = sys.getfilesystemencoding()
        for i, c in enumerate(command):
            if not isinstance(c, str):
                command[i] = c.encode(encoding)

        logger.debug("Running VPN with command: ")
        logger.debug("{0}".format(" ".join(command)))
        return command

    def getGateways(self):
        """
        Get the gateways from the appropiate launcher.

        :rtype: list
        """
        gateways_ports = self._launcher.get_gateways(
            self._eipconfig, self._providerconfig)

        # filter out ports since we don't need that info
        return [gateway for gateway, port in gateways_ports]

    # shutdown

    def killProcess(self):
        """
        Sends the KILL signal to the running process.
        """
        try:
            self.transport.signalProcess('KILL')
        except internet_error.ProcessExitedAlready:
            logger.debug('Process Exited Already')
