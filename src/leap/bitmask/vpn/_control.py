class VPNControl(object):
    """
    This is the high-level object that the service is dealing with.
    It exposes the start and terminate methods.

    On start, it spawns a VPNProcess instance that will use a vpnlauncher
    suited for the running platform and connect to the management interface
    opened by the openvpn process, executing commands over that interface on
    demand.
    """
    TERMINATE_MAXTRIES = 10
    TERMINATE_WAIT = 1  # secs

    OPENVPN_VERB = "openvpn_verb"

    def __init__(self, **kwargs):
        # TODO what the fuck this is doing that is different from
        # the manager?
        self._vpnproc = None
        self._pollers = []

        self._signaler = kwargs['signaler']
        # self._openvpn_verb = flags.OPENVPN_VERBOSITY
        self._openvpn_verb = None

        self._user_stopped = False
        self._remotes = kwargs['remotes']

    def start(self, *args, **kwargs):
        """
        Starts the openvpn subprocess.

        :param args: args to be passed to the VPNProcess
        :type args: tuple

        :param kwargs: kwargs to be passed to the VPNProcess
        :type kwargs: dict
        """
        logger.debug('VPN: start')
        self._user_stopped = False
        self._stop_pollers()
        kwargs['openvpn_verb'] = self._openvpn_verb
        kwargs['signaler'] = self._signaler
        kwargs['remotes'] = self._remotes

        # start the main vpn subprocess
        vpnproc = VPNProcess(*args, **kwargs)

        if vpnproc.get_openvpn_process():
            logger.info("Another vpn process is running. Will try to stop it.")
            vpnproc.stop_if_already_running()

        # FIXME it would be good to document where the
        # errors here are catched, since we currently handle them
        # at the frontend layer. This *should* move to be handled entirely
        # in the backend.
        # exception is indeed technically catched in backend, then converted
        # into a signal, that is catched in the eip_status widget in the
        # frontend, and converted into a signal to abort the connection that is
        # sent to the backend again.

        # the whole exception catching should be done in the backend, without
        # the ping-pong to the frontend, and without adding any logical checks
        # in the frontend. We should just communicate UI changes to frontend,
        # and abstract us away from anything else.
        try:
            cmd = vpnproc.getCommand()
        except Exception as e:
            logger.error("Error while getting vpn command... {0!r}".format(e))
            raise

        env = os.environ
        for key, val in vpnproc.vpn_env.items():
            env[key] = val

        reactor.spawnProcess(vpnproc, cmd[0], cmd, env)
        self._vpnproc = vpnproc

        # add pollers for status and state
        # this could be extended to a collection of
        # generic watchers

        poll_list = [LoopingCall(vpnproc.pollStatus),
                     LoopingCall(vpnproc.pollState)]
        self._pollers.extend(poll_list)
        self._start_pollers()


    # TODO -- rename to stop ??
    def terminate(self, shutdown=False, restart=False):
        """
        Stops the openvpn subprocess.

        Attempts to send a SIGTERM first, and after a timeout
        it sends a SIGKILL.

        :param shutdown: whether this is the final shutdown
        :type shutdown: bool
        :param restart: whether this stop is part of a hard restart.
        :type restart: bool
        """
        self._stop_pollers()

        # First we try to be polite and send a SIGTERM...
        if self._vpnproc is not None:
            # We assume that the only valid stops are initiated
            # by an user action, not hard restarts
            self._user_stopped = not restart
            self._vpnproc.is_restart = restart

            self._sentterm = True
            self._vpnproc.terminate_openvpn(shutdown=shutdown)

            # ...but we also trigger a countdown to be unpolite
            # if strictly needed.
            reactor.callLater(
                self.TERMINATE_WAIT, self._kill_if_left_alive)
        else:
            logger.debug("VPN is not running.")


    # TODO should this be public??
    def killit(self):
        """
        Sends a kill signal to the process.
        """
        self._stop_pollers()
        if self._vpnproc is None:
            logger.debug("There's no vpn process running to kill.")
        else:
            self._vpnproc.aborted = True
            self._vpnproc.killProcess()


    def bitmask_root_vpn_down(self):
        """
        Bring openvpn down using the privileged wrapper.
        """
        if IS_MAC:
            # We don't support Mac so far
            return True
        BM_ROOT = force_eval(linux.LinuxVPNLauncher.BITMASK_ROOT)

        # FIXME -- port to processProtocol
        exitCode = subprocess.call(["pkexec",
                                    BM_ROOT, "openvpn", "stop"])
        return True if exitCode is 0 else False


    def _kill_if_left_alive(self, tries=0):
        """
        Check if the process is still alive, and send a
        SIGKILL after a timeout period.

        :param tries: counter of tries, used in recursion
        :type tries: int
        """
        while tries < self.TERMINATE_MAXTRIES:
            if self._vpnproc.transport.pid is None:
                logger.debug("Process has been happily terminated.")
                return
            else:
                logger.debug("Process did not die, waiting...")

            tries += 1
            reactor.callLater(self.TERMINATE_WAIT,
                              self._kill_if_left_alive, tries)
            return

        # after running out of patience, we try a killProcess
        logger.debug("Process did not died. Sending a SIGKILL.")
        try:
            self.killit()
        except OSError:
            logger.error("Could not kill process!")


    def _start_pollers(self):
        """
        Iterate through the registered observers
        and start the looping call for them.
        """
        for poller in self._pollers:
            poller.start(VPNManager.POLL_TIME)


    def _stop_pollers(self):
        """
        Iterate through the registered observers
        and stop the looping calls if they are running.
        """
        for poller in self._pollers:
            if poller.running:
                poller.stop()
        self._pollers = []
