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

import os

import psutil

from twisted.internet import defer, reactor
from twisted.internet.endpoints import clientFromString, connectProtocol
from twisted.logger import Logger

from leap.bitmask.util import STANDALONE
from leap.bitmask.vpn.utils import first, force_eval
from leap.bitmask.vpn.privilege import LinuxPolicyChecker
from leap.bitmask.vpn.management import ManagementProtocol
from leap.bitmask.vpn.launcher import VPNLauncher


TERMINATE_MAXTRIES = 10
TERMINATE_WAIT = 1  # secs
RESTART_WAIT = 2  # secs

log = Logger()


class OpenVPNAlreadyRunning(Exception):
    message = ("Another openvpn instance is already running, and could "
               "not be stopped.")


class AlienOpenVPNAlreadyRunning(Exception):
    message = ("Another openvpn instance is already running, and could "
               "not be stopped because it was not launched by LEAP.")


def _maybe_get_running_openvpn():
    """
    Looks for previously running openvpn instances.

    :rtype: psutil Process
    """
    openvpn = None
    for p in psutil.process_iter():
        try:
            # This needs more work, see #3268, but for the moment
            # we need to be able to filter out arguments in the form
            # --openvpn-foo, since otherwise we are shooting ourselves
            # in the feet.

            cmdline = p.cmdline()
            if any(map(lambda s: s.find(
                    "LEAPOPENVPN") != -1, cmdline)):
                openvpn = p
                break
        except psutil.AccessDenied:
            pass
    return openvpn


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

        if os.getuid() != 0:
            policyChecker = LinuxPolicyChecker()
            pkexec = policyChecker.maybe_pkexec()
            if pkexec:
                command.insert(0, first(pkexec))

        return command

    def terminate_or_kill(self, terminatefun, killfun, proc):
        terminatefun()

        # we trigger a countdown to be unpolite
        # if strictly needed.
        d = defer.Deferred()
        reactor.callLater(
            TERMINATE_WAIT, self._wait_and_kill, killfun, proc, d)
        return d

    def _wait_and_kill(self, killfun, proc, deferred, tries=0):
        """
        Check if the process is still alive, and call the killfun
        after waiting several times during a timeout period.

        :param tries: counter of tries, used in recursion
        :type tries: int
        """
        if tries < TERMINATE_MAXTRIES:
            if proc.transport.pid is None:
                deferred.callback(True)
                return
            else:
                self.log.debug('Process did not die, waiting...')

            tries += 1
            reactor.callLater(
                TERMINATE_WAIT,
                self._wait_and_kill, killfun, proc, deferred, tries)
            return

        # after running out of patience, we try a killProcess
        d = killfun()
        d.addCallback(lambda _: deferred.callback(True))
        return d

    def kill_previous_openvpn(kls):
        """
        Checks if VPN is already running and tries to stop it.

        Might raise OpenVPNAlreadyRunning.

        :return: a deferred, that fires with True if stopped.
        """
        @defer.inlineCallbacks
        def gotProtocol(proto):
            return proto.signal('SIGTERM')

        def connect_to_management(path):
            # XXX this has a problem with connections to different
            # remotes. So the reconnection will only work when we are
            # terminating instances left running for the same provider.
            # If we are killing an openvpn instance configured for another
            # provider, we will get:
            # TLS Error: local/remote TLS keys are out of sync
            # However, that should be a rare case right now.
            endpoint = clientFromString(reactor, path)
            d = connectProtocol(endpoint, ManagementProtocol(verbose=False))
            d.addCallback(gotProtocol)
            return d

        def verify_termination(ignored):
            openvpn = _maybe_get_running_openvpn()
            if openvpn is None:
                log.debug('Successfully finished already running '
                          'openvpn process.')
                return True
            else:
                log.warn('Unable to terminate OpenVPN')
                raise OpenVPNAlreadyRunning

        openvpn = _maybe_get_running_openvpn()
        if not openvpn:
            log.debug('Could not find openvpn process while '
                      'trying to stop it.')
            return False

        log.debug('OpenVPN is already running, trying to stop it...')
        cmdline = openvpn.cmdline
        management = "--management"

        if isinstance(cmdline, list) and management in cmdline:
            # we know that our invocation has this distinctive fragment, so
            # we use this fingerprint to tell other invocations apart.
            # this might break if we change the configuration path in the
            # launchers

            def smellslikeleap(s):
                return "leap" in s and "providers" in s

            if not any(map(smellslikeleap, cmdline)):
                log.debug("We cannot stop this instance since we do not "
                          "recognise it as a leap invocation.")
                raise AlienOpenVPNAlreadyRunning

            try:
                index = cmdline.index(management)
                host = cmdline[index + 1]
                port = cmdline[index + 2]
                log.debug("Trying to connect to %s:%s"
                          % (host, port))

                if port == 'unix':
                    path = b"unix:path=%s" % host
                d = connect_to_management(path)
                d.addCallback(verify_termination)
                return d

            except (Exception, AssertionError):
                log.failure('Problem trying to terminate OpenVPN')
        else:
            log.debug('Could not find the expected openvpn command line.')
