import os
import shutil
import socket

from twisted.internet import reactor
from twisted.logger import Logger

import psutil
try:
    # psutil < 2.0.0
    from psutil.error import AccessDenied as psutil_AccessDenied
    PSUTIL_2 = False
except ImportError:
    # psutil >= 2.0.0
    from psutil import AccessDenied as psutil_AccessDenied
    PSUTIL_2 = True



class OpenVPNAlreadyRunning(Exception):
    message = ("Another openvpn instance is already running, and could "
               "not be stopped.")


class AlienOpenVPNAlreadyRunning(Exception):
    message = ("Another openvpn instance is already running, and could "
               "not be stopped because it was not launched by LEAP.")


class ImproperlyConfigured(Exception):
    pass


class Management(object):


    def terminate(self, shutdown=False):
        """
        Attempts to terminate openvpn by sending a SIGTERM.
        """
        if self.is_connected():
            self._send_command("signal SIGTERM")
        if shutdown:
            _cleanup_tempfiles()


# TODO -- finish porting ----------------------------------------------------

def _cleanup_tempfiles(self):
    """
    Remove all temporal files we might have left behind.

    Iif self.port is 'unix', we have created a temporal socket path that,
    under normal circumstances, we should be able to delete.
    """
    if self._socket_port == "unix":
        tempfolder = _first(os.path.split(self._host))
        if tempfolder and os.path.isdir(tempfolder):
            try:
                shutil.rmtree(tempfolder)
            except OSError:
                self.log.error(
                    'Could not delete tmpfolder %s' % tempfolder)

def _get_openvpn_process():
    """
    Looks for openvpn instances running.

    :rtype: process
    """
    openvpn_process = None
    for p in psutil.process_iter():
        try:
            # XXX Not exact!
            # Will give false positives.
            # we should check that cmdline BEGINS
            # with openvpn or with our wrapper
            # (pkexec / osascript / whatever)

            # This needs more work, see #3268, but for the moment
            # we need to be able to filter out arguments in the form
            # --openvpn-foo, since otherwise we are shooting ourselves
            # in the feet.

            if PSUTIL_2:
                cmdline = p.cmdline()
            else:
                cmdline = p.cmdline
            if any(map(lambda s: s.find(
                    "LEAPOPENVPN") != -1, cmdline)):
                openvpn_process = p
                break
        except psutil_AccessDenied:
            pass
    return openvpn_process

def _stop_if_already_running():
    """
    Checks if VPN is already running and tries to stop it.

    Might raise OpenVPNAlreadyRunning.

    :return: True if stopped, False otherwise

    """
    process = _get_openvpn_process()
    if not process:
        self.log.debug('Could not find openvpn process while '
                       'trying to stop it.')
        return

    log.debug('OpenVPN is already running, trying to stop it...')
    cmdline = process.cmdline

    manag_flag = "--management"

    if isinstance(cmdline, list) and manag_flag in cmdline:

        # we know that our invocation has this distinctive fragment, so
        # we use this fingerprint to tell other invocations apart.
        # this might break if we change the configuration path in the
        # launchers

        def smellslikeleap(s):
            return "leap" in s and "providers" in s

        if not any(map(smellslikeleap, cmdline)):
            self.log.debug("We cannot stop this instance since we do not "
                           "recognise it as a leap invocation.")
            raise AlienOpenVPNAlreadyRunning

        try:
            index = cmdline.index(manag_flag)
            host = cmdline[index + 1]
            port = cmdline[index + 2]
            self.log.debug("Trying to connect to %s:%s"
                           % (host, port))
            _connect()

            # XXX this has a problem with connections to different
            # remotes. So the reconnection will only work when we are
            # terminating instances left running for the same provider.
            # If we are killing an openvpn instance configured for another
            # provider, we will get:
            # TLS Error: local/remote TLS keys are out of sync
            # However, that should be a rare case right now.
            self._send_command("signal SIGTERM")
        except (Exception, AssertionError):
            log.failure('Problem trying to terminate OpenVPN')
    else:
        log.debug('Could not find the expected openvpn command line.')

    process = _get_openvpn_process()
    if process is None:
        self.log.debug('Successfully finished already running '
                       'openvpn process.')
        return True
    else:
        self.log.warn('Unable to terminate OpenVPN')
        raise OpenVPNAlreadyRunning
