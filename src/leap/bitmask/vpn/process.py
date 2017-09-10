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
import sys

from twisted.internet import protocol, reactor, defer
from twisted.internet import error as internet_error
from twisted.internet.endpoints import clientFromString, connectProtocol
from twisted.logger import Logger
from zope.interface import implementer

from leap.bitmask.vpn.utils import get_vpn_launcher
from leap.bitmask.vpn.management import ManagementProtocol, IStateListener
from leap.bitmask.vpn.launchers import darwin
from leap.bitmask.vpn.constants import IS_MAC, IS_LINUX

from leap.common.events import catalog, emit_async


OPENVPN_VERBOSITY = 4


@implementer(IStateListener)
class VPNStateListener(object):

    # TODO we should move the state history to this class
    # and make VPNProcess the implementer itself - or the service.

    def change_state(self, state):
        emit_async(catalog.VPN_STATUS_CHANGED)


class _VPNProcess(protocol.ProcessProtocol):

    """
    A ProcessProtocol class that can be used to spawn a process that will
    launch openvpn and connect to its management interface to control it
    programmatically.
    """

    log = Logger()

    # HACK - reactor is expected to set this up when the process is spawned.
    # should try to get it from the management protocol instead.
    # XXX or, at least, we can check if they match.
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
        """
        self._host = socket_host
        self._port = socket_port

        if socket_port == 'unix':
            folder = os.path.split(self._host)[0]
            if not os.path.isdir(folder):
                os.makedirs(folder)
            self._management_endpoint = clientFromString(
                reactor, b"unix:path=%s" % socket_host)
        else:
            raise ValueError('tcp endpoint not configured')

        self._vpnconfig = vpnconfig
        self._providerconfig = providerconfig
        self._launcher = get_vpn_launcher()
        self._restartfun = restartfun
        self._status = 'off'

        self.restarting = True
        self.failed = False
        self.errmsg = None
        self.proto = None
        self._remotes = remotes

    # processProtocol methods

    def outReceived(self, data):
        # use this to debug failed invocations.
        # print("DEBUG VPN: %s" % data)
        pass

    @defer.inlineCallbacks
    def _got_management_protocol(self, proto):
        self.proto = proto
        listener = VPNStateListener()
        proto.addStateListener(listener)

        try:
            yield proto.logOn()
            yield proto.getVersion()
            yield proto.getPid()
            yield proto.stateOn()
            yield proto.byteCount(2)
        except Exception as exc:
            print('[!] Error: %s' % exc)

    def _connect_to_management(self, retries=30):
        if retries == 0:
            self.log.error('Timeout whilte connecting to management')
            self.failed = True
            return

        def retry(retries):
            ctr = retries - 1
            self.log.warn(
                'Error connecting to management, retrying. '
                'Retries left:  %s' % ctr)
            reactor.callLater(
                0.1, self._connect_to_management, ctr)

        self._d = connectProtocol(
            self._management_endpoint,
            ManagementProtocol(verbose=True))
        self._d.addCallbacks(
            self._got_management_protocol,
            lambda f: retry(retries))

    def connectionMade(self):
        self.failed = False
        reactor.callLater(0.1, self._connect_to_management)

    def processExited(self, failure):
        err = failure.trap(
            internet_error.ProcessDone, internet_error.ProcessTerminated)

        if err == internet_error.ProcessDone:
            pass

        elif err == internet_error.ProcessTerminated:
            self.failed = True
            self.errmsg = failure.value.exitCode
            if self.errmsg:
                self.log.debug('Process Exited, status %d' % (self.errmsg,))
            else:
                self.log.warn('%r' % failure.value)
        if IS_MAC:
            # TODO: need to exit properly!
            self.errmsg = None
        self.proto = None

    def processEnded(self, reason):
        """
        Called when the child process exits and all file descriptors associated
        with it have been closed.
        """
        self.proto = None
        exit_code = reason.value.exitCode

        if isinstance(exit_code, int):
            self.log.debug('processEnded, status %d' % (exit_code,))
            if self.restarting:
                self.log.debug('Restarting VPN process')
                self._cleanup()
                self._restartfun()

    def _cleanup(self):
        """
        Remove all temporal files we might have left behind.

        Iif self.port is 'unix', we have created a temporal socket path that,
        under normal circumstances, we should be able to delete.
        """
        if self._port == "unix":
            tempfolder = os.path.split(self._host)[0]
            if tempfolder and os.path.isdir(tempfolder):
                try:
                    shutil.rmtree(tempfolder)
                except OSError:
                    self.log.error(
                        'Could not delete VPN temp folder %s' % tempfolder)

    # status handling

    @property
    def status(self):
        if self.failed:
            return {'status': 'failed', 'error': self.errmsg}
        if not self.proto:
            return {'status': 'off', 'error': None}

        try:
            self._status = self.proto.state.simple.lower()
            status = {'status': self._status, 'error': None}
        except AttributeError:
            # glitch due to proto.state transition?
            status = {'status': self._status, 'error': None}

        if self.proto.traffic:
            remote = self.proto.remote
            rport = self.proto.rport
            status['remote'] = '%s:%s' % (remote, rport)
            down, up = self.proto.traffic.get_rate()
            status['up'] = up
            status['down'] = down
        if status['status'] == 'off' and self.restarting:
            status['status'] = 'starting'
        return status

    # launcher

    def preUp(self):
        self._launcher.kill_previous_openvpn()

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
            remotes=self._remotes)

        encoding = sys.getfilesystemencoding()
        for i, c in enumerate(command):
            if not isinstance(c, str):
                command[i] = c.encode(encoding)

        self.log.debug("Running VPN with command: ")
        self.log.debug("{0}".format(" ".join(command)))
        return command

    # shutdown

    def terminate(self):
        if self.proto:
            self.proto.signal('SIGTERM')

    def kill(self):
        try:
            self.transport.signalProcess('KILL')
        except internet_error.ProcessExitedAlready:
            self.log.debug('Process Exited Already')

    def terminate_or_kill(self):
        return self._launcher.terminate_or_kill(
            self.terminate, self.kill, self)


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
