from itertools import chain, repeat

from leap.common.events import catalog, emit_async

from leap.bitmask.vpn._human import bytes2human

# TODO implement a more explicit state machine
# TODO check good transitions
# TODO check valid states


class VPNStatus(object):
    """
    A class containing different patterns in the openvpn output that
    we can react upon. The patterns drive an internal state machine that can be
    queried through the ``status`` property.
    """

    _events = {
        'NETWORK_UNREACHABLE': (
            'Network is unreachable (code=101)',),
        'PROCESS_RESTART_TLS': (
            "SIGTERM[soft,tls-error]",),
        'INITIALIZATION_COMPLETED': (
            "Initialization Sequence Completed",),
    }
    _STARTING = ('AUTH', 'WAIT', 'CONNECTING', 'GET_CONFIG',
                 'ASSIGN_IP', 'ADD_ROUTES', 'RECONNECTING')
    _STOPPING = ("EXITING",)
    _CONNECTED = ("CONNECTED",)

    def __init__(self):
        self._status = 'off'
        self.errcode = None
        self._traffic_down = None
        self._traffic_up = None
        self._chained_iter = chain(*[
            zip(repeat(key, len(l)), l)
            for key, l in self._events.iteritems()])

    def _status_codes(self, event):

        _table = {
            "network_unreachable": ('off', 'network unreachable'),
            "process_restart_tls": ('starting', 'restart tls'),
            "initialization_completed": ('on', None)
        }
        return _table.get(event.lower())

    def watch(self, line):
        for event, pattern in self._chained_iter:
            if pattern in line:
                break
        else:
            return

        status, errcode = self._status_codes(event)
        self.set_status(status, errcode)

    @property
    def status(self):
        status = self.get_traffic_status()
        status.update({
            'status': self._status,
            'error': self.errcode
        })
        return status

    def set_status(self, status, errcode):
        if not status:
            return

        if status in self._STARTING:
            status = "starting"
        elif status in self._STOPPING:
            status = "stopping"
        elif status in self._CONNECTED:
            status = "on"

        if self._status != status:
            self._status = status
            self.errcode = errcode
            emit_async(catalog.VPN_STATUS_CHANGED)

    def get_traffic_status(self):
        down = None
        up = None
        if self._traffic_down:
            down = bytes2human(self._traffic_down)
        if self._traffic_up:
            up = bytes2human(self._traffic_up)
        return {'down': down, 'up': up}

    def set_traffic_status(self, up, down):
        if up != self._traffic_up or down != self._traffic_down:
            self._traffic_up = up
            self._traffic_down = down
            emit_async(catalog.VPN_STATUS_CHANGED)
