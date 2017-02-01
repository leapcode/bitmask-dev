from itertools import chain, repeat
from twisted.logger import Logger

logger = Logger()


class VPNObserver(object):
    """
    A class containing different patterns in the openvpn output that
    we can react upon.
    """

    _events = {
        'NETWORK_UNREACHABLE': (
            'Network is unreachable (code=101)',),
        'PROCESS_RESTART_TLS': (
            "SIGTERM[soft,tls-error]",),
        'PROCESS_RESTART_PING': (
            "SIGTERM[soft,ping-restart]",),
        'INITIALIZATION_COMPLETED': (
            "Initialization Sequence Completed",),
    }

    def __init__(self, signaler=None):
        self._signaler = signaler

    def watch(self, line):
        """
        Inspects line searching for the different patterns. If a match
        is found, try to emit the corresponding signal.

        :param line: a line of openvpn output
        :type line: str
        """
        chained_iter = chain(*[
            zip(repeat(key, len(l)), l)
            for key, l in self._events.iteritems()])
        for event, pattern in chained_iter:
            if pattern in line:
                logger.debug('pattern matched! %s' % pattern)
                break
        else:
            return

        sig = self._get_signal(event)
        if sig is not None:
            if self._signaler is not None:
                self._signaler.signal(sig)
            return
        else:
            logger.debug('We got %s event from openvpn output but we could '
                         'not find a matching signal for it.' % event)

    def _get_signal(self, event):
        """
        Tries to get the matching signal from the eip signals
        objects based on the name of the passed event (in lowercase)

        :param event: the name of the event that we want to get a signal for
        :type event: str
        :returns: a Signaler signal or None
        :rtype: str or None
        """
        if self._signaler is None:
            return
        sig = self._signaler
        signals = {
            "network_unreachable": sig.eip_network_unreachable,
            "process_restart_tls": sig.eip_process_restart_tls,
            "process_restart_ping": sig.eip_process_restart_ping,
            "initialization_completed": sig.eip_connected
        }
        return signals.get(event.lower())
