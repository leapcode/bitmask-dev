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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
VPN Tunnel.
"""

import os
import tempfile

from twisted.internet import reactor, defer
from twisted.logger import Logger

from ._config import _TempVPNConfig, _TempProviderConfig
from .constants import IS_WIN, IS_LINUX
from .process import VPNProcess


# TODO gateway selection should be done in this class.


# TODO ----------------- refactor --------------------
# [ ] register change state listener
# emit_async(catalog.VPN_STATUS_CHANGED)
# [ ] catch ping-restart
# 'NETWORK_UNREACHABLE': (
#    'Network is unreachable (code=101)',),
# 'PROCESS_RESTART_TLS': (
#    "SIGTERM[soft,tls-error]",),


class ConfiguredTunnel(object):

    """
    A ConfiguredTunne holds the configuration for a VPN connection, and allows
    to control that connection.

    This is the high-level object that the service knows about.
    It exposes the start and terminate methods for the VPN Tunnel.

    On start, it spawns a VPNProcess instance that will use a vpnlauncher
    suited for the running platform and connect to the management interface
    opened by the openvpn process, executing commands over that interface on
    demand.
    """

    TERMINATE_MAXTRIES = 10
    TERMINATE_WAIT = 1  # secs
    RESTART_WAIT = 2  # secs

    log = Logger()

    def __init__(self, provider, remotes, cert_path, key_path, ca_path,
                 extra_flags):
        """
        :param remotes: a list of gateways tuple (ip, port) looking like this:
            ((ip1, portA), (ip2, portB), ...)
        :type remotes: tuple of tuple(str, int)
        """
        self._remotes = remotes
        ports = []

        self._vpnconfig = _TempVPNConfig(extra_flags, cert_path, ports)
        self._providerconfig = _TempProviderConfig(provider, ca_path)

        host, port = _get_management_location()
        self._host = host
        self._port = port

        self._vpnproc = None
        self._user_stopped = False

    def start(self):
        return self._start_vpn()

    def stop(self):
        return self._stop_vpn(shutdown=False, restart=False)

    #  status

    @property
    def status(self):
        if not self._vpnproc:
            return {'status': 'off', 'error': None}
        return self._vpnproc.status

    @property
    def traffic_status(self):
        return self._vpnproc.traffic_status

    # VPN Control

    def _start_vpn(self):
        self.log.debug('VPN: start')

        self._user_stopped = False

        args = [self._vpnconfig, self._providerconfig, self._host,
                self._port]
        kwargs = {'openvpn_verb': 4, 'remotes': self._remotes,
                  'restartfun': self.restart}
        vpnproc = VPNProcess(*args, **kwargs)

        try:
            vpnproc.preUp()
        except Exception as e:
            self.log.error('Error on vpn pre-up {0!r}'.format(e))
            raise
        try:
            cmd = vpnproc.getCommand()
        except Exception as e:
            self.log.error(
                'Error while getting vpn command... {0!r}'.format(e))
            raise

        env = os.environ
        try:
            runningproc = reactor.spawnProcess(vpnproc, cmd[0], cmd, env)
        except Exception as e:
            self.log.error(
                'Error while spawning vpn process... {0!r}'.format(e))
            return False

        # TODO get pid from management instead
        vpnproc.pid = runningproc.pid
        self._vpnproc = vpnproc
        return True

    @defer.inlineCallbacks
    def _restart_vpn(self):
        yield self.stop(shutdown=False, restart=True)
        reactor.callLater(
            self.RESTART_WAIT, self.start)

    def _stop_vpn(self, shutdown=False, restart=False):
        """
        Stops the openvpn subprocess.

        Attempts to send a SIGTERM first, and after a timeout
        it sends a SIGKILL.

        :param shutdown: whether this is the final shutdown
        :type shutdown: bool
        :param restart: whether this stop is part of a hard restart.
        :type restart: bool
        """
        # TODO how to return False if this fails
        # XXX maybe return a deferred

        # We assume that the only valid stops are initiated
        # by an user action, not hard restarts
        self._user_stopped = not restart
        if self._vpnproc is not None:
            self._vpnproc.restarting = restart

        try:
            if self._vpnproc is not None:
                self._vpnproc.preDown()
        except Exception as e:
            self.log.error('Error on vpn pre-down {0!r}'.format(e))
            raise

        d = defer.succeed(True)
        if IS_LINUX:
            # TODO factor this out to a linux-only launcher mechanism.
            # First we try to be polite and send a SIGTERM...
            if self._vpnproc is not None:
                self._sentterm = True
                self._vpnproc.terminate()

                # we trigger a countdown to be unpolite
                # if strictly needed.
                d = defer.Deferred()
                reactor.callLater(
                    self.TERMINATE_WAIT, self._kill_if_left_alive, d)
        return d

    def _wait_and_kill(self, deferred, tries=0):
        """
        Check if the process is still alive, and send a
        SIGKILL after a waiting several times during a timeout period.

        :param tries: counter of tries, used in recursion
        :type tries: int
        """
        if tries < self.TERMINATE_MAXTRIES:
            if self._vpnproc.transport.pid is None:
                deferred.callback(True)
                return
            else:
                self.log.debug('Process did not die, waiting...')

            tries += 1
            reactor.callLater(
                self.TERMINATE_WAIT,
                self._wait_and_kill, deferred, tries)
            return

        # after running out of patience, we try a killProcess
        self._kill(deferred)

    def _kill(self, d):
        self.log.debug('Process did not die. Sending a SIGKILL.')
        try:
            if self._vpnproc is None:
                self.log.debug("There's no vpn process running to kill.")
            else:
                self._vpnproc.aborted = True
                self._vpnproc.kill()
        except OSError:
            self.log.error('Could not kill process!')
        d.callback(True)


# utils


def _get_management_location():
    """
    Return a tuple with the host (socket) and port to be used for VPN.

    :return: (host, port)
    :rtype: tuple (str, str)
    """
    if IS_WIN:
        host = "localhost"
        port = "9876"
    else:
        host = os.path.join(
            tempfile.mkdtemp(prefix="leap-tmp"), 'openvpn.socket')
        port = "unix"
    return host, port
