from itertools import chain, repeat
from ._human import bytes2human

from leap.common.events import catalog, emit_async


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
        'INITIALIZATION_COMPLETED': (
            "Initialization Sequence Completed",),
    }

    def __init__(self):
        self._status = 'off'
        self.errcode = None
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
        if status in ("AUTH", "WAIT", "CONNECTING", "GET_CONFIG",
                      "ASSIGN_IP", "ADD_ROUTES", "RECONNECTING"):
            status = "starting"
        elif status == "EXITING":
            status = "stopping"
        elif status == "CONNECTED":
            status = "on"

        self._status = status
        self.errcode = errcode
        emit_async(catalog.VPN_STATUS_CHANGED)

    def set_traffic_status(self, status):
        up, down = status
        self._traffic_up = up
        self._traffic_down = down

    def get_traffic_status(self):
        down = None
        up = None
        if self._traffic_down:
            down = bytes2human(self._traffic_down)
        if self._traffic_up:
            up = bytes2human(self._traffic_up)
        return {'down': down, 'up': up}

    @property
    def status(self):
        status = self.get_traffic_status()
        status.update({
            'status': self._status,
            'error': self.errcode
        })
        return status

    def _status_codes(self, event):
        # TODO check good transitions
        # TODO check valid states

        _table = {
            "network_unreachable": ('off', 'network unreachable'),
            "process_restart_tls": ('starting', 'restart tls'),
            "initialization_completed": ('on', None)
        }
        return _table.get(event.lower())
