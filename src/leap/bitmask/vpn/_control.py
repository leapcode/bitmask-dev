import os

from twisted.internet import reactor, defer
from twisted.logger import Logger

from .process import VPNProcess
from .constants import IS_LINUX


# TODO
# TODO merge these classes with service.
# [ ] register change state listener
# emit_async(catalog.VPN_STATUS_CHANGED)
# [ ] catch ping-restart
# 'NETWORK_UNREACHABLE': (
#    'Network is unreachable (code=101)',),
# 'PROCESS_RESTART_TLS': (
#    "SIGTERM[soft,tls-error]",),


class VPNControl(object):

    """
    This is the high-level object that the service knows about.
    It exposes the start and terminate methods.

    On start, it spawns a VPNProcess instance that will use a vpnlauncher
    suited for the running platform and connect to the management interface
    opened by the openvpn process, executing commands over that interface on
    demand.
    """

    TERMINATE_MAXTRIES = 10
    TERMINATE_WAIT = 1  # secs
    RESTART_WAIT = 2  # secs

    log = Logger()

    def __init__(self, remotes, vpnconfig,
                 providerconfig, socket_host, socket_port):
        self._vpnproc = None
        self._user_stopped = False

        self._remotes = remotes
        self._vpnconfig = vpnconfig
        self._providerconfig = providerconfig
        self._host = socket_host
        self._port = socket_port

    def start(self):
        self.log.debug('VPN: start')

        self._user_stopped = False

        args = [self._vpnconfig, self._providerconfig, self._host,
                self._port]
        kwargs = {'openvpn_verb': 4, 'remotes': self._remotes,
                  'restartfun': self.restart}

        vpnproc = VPNProcess(*args, **kwargs)

        # TODO -- restore
        # if get_openvpn_process():
        #    self.log.info(
        #        'Another vpn process is running. Will try to stop it.')
        #    vpnproc.stop_if_already_running()

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
    def restart(self):
        yield self.stop(shutdown=False, restart=True)
        reactor.callLater(
            self.RESTART_WAIT, self.start)

    def stop(self, shutdown=False, restart=False):
        """
        Stops the openvpn subprocess.

        Attempts to send a SIGTERM first, and after a timeout
        it sends a SIGKILL.

        :param shutdown: whether this is the final shutdown
        :type shutdown: bool
        :param restart: whether this stop is part of a hard restart.
        :type restart: bool
        """
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

    # TODO -- remove indirection
    @property
    def status(self):
        if not self._vpnproc:
            return {'status': 'off', 'error': None}
        return self._vpnproc.status

    @property
    def traffic_status(self):
        return self._vpnproc.traffic_status

    def _killit(self):
        if self._vpnproc is None:
            self.log.debug("There's no vpn process running to kill.")
        else:
            self._vpnproc.aborted = True
            self._vpnproc.kill()

    def _kill_if_left_alive(self, deferred, tries=0):
        """
        Check if the process is still alive, and send a
        SIGKILL after a timeout period.

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
            reactor.callLater(self.TERMINATE_WAIT,
                              self._kill_if_left_alive, deferred, tries)
            return

        # after running out of patience, we try a killProcess
        self.log.debug('Process did not die. Sending a SIGKILL.')
        try:
            self._killit()
        except OSError:
            self.log.error('Could not kill process!')
        deferred.callback(True)
