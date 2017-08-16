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

import sys

from twisted.internet import protocol, reactor
from twisted.internet import error as internet_error
from twisted.logger import Logger

from leap.bitmask.vpn.utils import get_vpn_launcher
from leap.bitmask.vpn._status import VPNStatus
from leap.bitmask.vpn._management import VPNManagement

from leap.bitmask.vpn.launchers import darwin
from leap.bitmask.vpn.constants import IS_MAC, IS_LINUX


# OpenVPN verbosity level - from flags.py
OPENVPN_VERBOSITY = 1


class _VPNProcess(protocol.ProcessProtocol):

    """
    A ProcessProtocol class that can be used to spawn a process that will
    launch openvpn and connect to its management interface to control it
    programmatically.
    """

    log = Logger()

    # HACK - reactor is expected to set this up when the process is spawned.
    # should try to get it from within this class.
    pid = None

    # TODO do we really need the vpnconfig/providerconfig objects in here???

    def __init__(self, vpnconfig, providerconfig, socket_host, socket_port,
                 openvpn_verb, remotes, restartfun=None):
        """
        :param vpnconfig: vpn configuration object
        :type vpnconfig: VPNConfig

        :param providerconfig: provider specific configuration
        :type providerconfig: ProviderConfig

        :param socket_host: either socket path (unix) or socket IP
        :type socket_host: str

        :param socket_port: either string "unix" if it's a unix
                            socket, or port otherwise
        :type socket_port: str

        :param openvpn_verb: the desired level of verbosity in the
                             openvpn invocation
        :type openvpn_verb: int
        """
        self._management = VPNManagement()
        self._management.set_connection(socket_host, socket_port)
        self._host = socket_host
        self._port = socket_port

        self._vpnconfig = vpnconfig
        self._providerconfig = providerconfig
        self._launcher = get_vpn_launcher()

        self._alive = False

        # XXX use flags, maybe, instead of passing
        # the parameter around.
        self._openvpn_verb = openvpn_verb
        self._restartfun = restartfun

        self._status = VPNStatus()
        self._management.set_watcher(self._status)

        self.restarting = True
        self._remotes = remotes

    @property
    def status(self):
        status = self._status.status
        if status['status'] == 'off' and self.restarting:
            status['status'] = 'starting'
        return status

    @property
    def traffic_status(self):
        return self._status.get_traffic_status()

    # processProtocol methods

    def connectionMade(self):
        """
        Called when the connection is made.
        """
        self._alive = True
        self.aborted = False
        self._management.connect_retry(max_retries=10)

    def outReceived(self, data):
        """
        Called when new data is available on stdout.
        We only use this to drive the status state machine in linux, OSX uses
        the management interface.

        :param data: the data read on stdout
        """
        # TODO deprecate, use log through management  interface too.

        if IS_LINUX:
            # truncate the newline
            line = data[:-1]
            # TODO -- internalize this into _status!!! so that it can be shared
            if 'SIGTERM[soft,ping-restart]' in line:
                self.restarting = True

    def processExited(self, failure):
        """
        Called when the child process exits.
        """
        err = failure.trap(
            internet_error.ProcessDone, internet_error.ProcessTerminated)

        if err == internet_error.ProcessDone:
            status, errmsg = 'off', None
        elif err == internet_error.ProcessTerminated:
            status, errmsg = 'failure', failure.value.exitCode
            if errmsg:
                self.log.debug('Process Exited, status %d' % (errmsg,))
            else:
                self.log.warn('%r' % failure.value)

        if IS_MAC:
            # TODO: need to exit properly!
            status, errmsg = 'off', None

        self._status.set_status(status, errmsg)
        self._alive = False

    def processEnded(self, reason):
        """
        Called when the child process exits and all file descriptors associated
        with it have been closed.
        """
        exit_code = reason.value.exitCode
        if isinstance(exit_code, int):
            self.log.debug('processEnded, status %d' % (exit_code,))
            if self.restarting:
                self.log.debug('Restarting VPN process')
                self._restartfun()

    # polling

    def pollStatus(self):
        """
        Polls connection status.
        """
        if self._alive:
            try:
                up, down = self._management.get_traffic_status()
                self._status.set_traffic_status(up, down)
            except Exception:
                self.log.debug('Could not parse traffic status')

    def pollState(self):
        """
        Polls connection state.
        """
        if self._alive:
            try:
                state = self._management.get_state()
                self._status.set_status(state, None)
            except Exception:
                self.log.debug('Could not parse connection state')

    def pollLog(self):
        if self._alive:
            try:
                self._management.process_log()
            except Exception:
                self.log.debug('Could not parse log')

    # launcher

    def preUp(self):
        pass

    def preDown(self):
        pass

    def getCommand(self):
        """
        Gets the vpn command from the aproppriate launcher.

        Might throw:
            VPNLauncherException,
            OpenVPNNotFoundException.

        :rtype: list of str
        """
        command = self._launcher.get_vpn_command(
            vpnconfig=self._vpnconfig,
            providerconfig=self._providerconfig,
            socket_host=self._host,
            socket_port=self._port,
            openvpn_verb=self._openvpn_verb,
            remotes=self._remotes)

        encoding = sys.getfilesystemencoding()
        for i, c in enumerate(command):
            if not isinstance(c, str):
                command[i] = c.encode(encoding)

        self.log.debug("Running VPN with command: ")
        self.log.debug("{0}".format(" ".join(command)))
        return command

    def get_openvpn_process(self):
        return self._management.get_openvpn_process()

    # shutdown

    def stop_if_already_running(self):
        return self._management.stop_if_already_running()

    def terminate(self, shutdown=False):
        self._management.terminate(shutdown)

    def killProcess(self):
        """
        Sends the KILL signal to the running process.
        """
        try:
            self.transport.signalProcess('KILL')
        except internet_error.ProcessExitedAlready:
            self.log.debug('Process Exited Already')


if IS_LINUX:

    VPNProcess = _VPNProcess

elif IS_MAC:

    class _VPNCanary(_VPNProcess):

        """
        Special form of _VPNProcess, for Darwin Launcher (windows might end up
        using the same strategy).

        This is a Canary Process that does not run openvpn itself, but it's
        notified by the privileged process when the process dies.

        This is a workaround to allow the state machine to be notified when
        openvpn process is spawned by the privileged helper.
        """

        def setupHelper(self):
            # TODO use get_vpn_launcher instead
            self.helper = darwin.HelperCommand()

        def preUp(self):
            self.setupHelper()
            cmd = self.getVPNCommand()
            self.helper.send('openvpn_start %s' % ' '.join(cmd))

        def preDown(self):
            self.helper.send('openvpn_stop')

        def connectionMade(self):
            self.setupHelper()
            reactor.callLater(2, self.registerPID)
            _VPNProcess.connectionMade(self)

        def registerPID(self):
            cmd = 'openvpn_set_watcher %s' % self.pid
            self.helper.send(cmd)

        def killProcess(self):
            cmd = 'openvpn_force_stop'
            self.helper.send(cmd)

        def getVPNCommand(self):
            vpncmd = _VPNProcess.getCommand(self)
            return vpncmd

        def getCommand(self):
            canary = '''import sys, signal, time
def receive_signal(signum, stack): sys.exit()
signal.signal(signal.SIGTERM, receive_signal)
while True: time.sleep(90)'''
            return ['python', '-c', '%s' % canary]

    VPNProcess = _VPNCanary
