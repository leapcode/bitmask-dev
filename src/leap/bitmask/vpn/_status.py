from itertools import chain, repeat
from twisted.logger import Logger
from ._human import bytes2human

logger = Logger()



# TODO implement a state machine in this class


class VPNStatus(object):
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

    def __init__(self):
        self.status = 'OFFLINE'
        self._traffic_down = None
        self._traffic_up = None

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
                break
        else:
            return

        status, errcode = self._status_codes(event)
        self.set_status(status, errcode)

    def set_status(self, status, errcode):
        self.status = status
        self.errcode = errcode

    def set_traffic_status(self, status):
        up, down = status
        self._traffic_up = up
        self._traffic_down = down

    def get_traffic_status(self):
        return {'down': bytes2human(self._traffic_down),
                'up': bytes2human(self._traffic_up)}

    def _status_codes(self, event):
        # TODO check good transitions
        # TODO check valid states

        _table = {
            "network_unreachable": ('OFFLINE', 'network unreachable'),
            "process_restart_tls": ('RESTARTING', 'restart tls'),
            "process_restart_ping": ('CONNECTING', None),
            "initialization_completed": ('ONLINE', None)
        }
        return _table.get(event.lower())
