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
from .constants import IS_WIN
from .process import VPNProcess


# The restarts are not really needed, since we're configuring
# openvpn to restart itself after a period of inactivity. However, if the
# openvpn process is killed by whatever reason, # we'll automatically try to
# restart the process.

RESTART_WAIT = 2  # in secs


class ConfiguredTunnel(object):

    """
    A ConfiguredTunnel holds the configuration for a VPN connection, and allows
    to control that connection.

    This is the high-level object that the service knows about.
    It exposes the start and terminate methods for the VPN Tunnel.

    On start, it spawns a VPNProcess instance that will use a vpnlauncher
    suited for the running platform and connect to the management interface
    opened by the openvpn process, executing commands over that interface on
    demand
    """

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

    @defer.inlineCallbacks
    def start(self):
        started = yield self._start_vpn()
        defer.returnValue(started)

    @defer.inlineCallbacks
    def stop(self, restart=False):
        stopped = yield self._stop_vpn(restart=restart)
        defer.returnValue(stopped)

    #  status

    @property
    def status(self):
        if not self._vpnproc:
            status = {'status': 'off', 'error': None}
        else:
            status = self._vpnproc.status
        # Currently, there's some UI flickering that needs to be debugged #9049
        # XXX remove this print after that.
        print ">>>STATUS", status
        return status

    @property
    def traffic_status(self):
        return self._vpnproc.traffic_status

    # VPN Control

    @defer.inlineCallbacks
    def _start_vpn(self):
        try:
            self.log.debug('VPN: start')
            args = [self._vpnconfig, self._providerconfig,
                    self._host, self._port]
            kwargs = {'openvpn_verb': 4, 'remotes': self._remotes,
                      'restartfun': self._restart_vpn}
            vpnproc = VPNProcess(*args, **kwargs)
            self._vpnproc = vpnproc

            self.__start_pre_up(vpnproc)
            cmd = self.__start_get_cmd(vpnproc)
            running = yield self.__start_spawn_proc(vpnproc, cmd)
            vpnproc.pid = running.pid
            defer.returnValue(True)
        except Exception as exc:
            self._vpnproc.failed = True
            self._vpnproc.errmsg = exc.message
            raise

    def __start_pre_up(self, proc):
        try:
            proc.preUp()
        except Exception as exc:
            self.log.error('Error on vpn pre-up {0!r}'.format(exc))
            raise

    def __start_get_cmd(self, proc):
        try:
            cmd = proc.getCommand()
        except Exception as exc:
            self.log.error(
                'Error while getting vpn command... {0!r}'.format(exc))
            raise exc
        return cmd

    def __start_spawn_proc(self, proc, cmd):
        env = os.environ
        try:
            running_p = reactor.spawnProcess(proc, cmd[0], cmd, env)
        except Exception as exc:
            self.log.error(
                'Error while spawning vpn process... {0!r}'.format(exc))
            raise exc
        return running_p

    @defer.inlineCallbacks
    def _restart_vpn(self):
        yield self.stop(restart=True)
        reactor.callLater(
            RESTART_WAIT, self.start)

    @defer.inlineCallbacks
    def _stop_vpn(self, restart=False):
        """
        Stops the openvpn subprocess.

        Attempts to send a SIGTERM first, and after a timeout
        it sends a SIGKILL.

        :param restart: whether this stop is part of a hard restart.
        :type restart: bool
        """
        # TODO how to return False if this fails
        # XXX maybe return a deferred

        if self._vpnproc is None:
            self.log.debug('Tried to stop VPN but no process found')
            defer.returnValue(False)

        self._vpnproc.restarting = restart
        self.__stop_pre_down(self._vpnproc)
        stopped = yield self._vpnproc.terminate_or_kill()
        defer.returnValue(stopped)

    def __stop_pre_down(self, proc):
        try:
            proc.preDown()
        except Exception as e:
            self.log.error('Error on vpn pre-down {0!r}'.format(e))
            raise


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
