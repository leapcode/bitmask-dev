#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Queue used to store status changes on EIP/VPN/Firewall and to be checked for
any app using this vpn library.

This should be considered a temporary code meant to replace the signaling
system that announces events inside of vpn code and is catched on the bitmask
client.
"""

import Queue


class StatusQueue(object):
    def __init__(self):
        self._status = Queue.Queue()

        # this attributes serve to simulate events in the old signaler used
        self.eip_network_unreachable = "network_unreachable"
        self.eip_process_restart_tls = "process_restart_tls"
        self.eip_process_restart_ping = "process_restart_ping"
        self.eip_connected = "initialization_completed"
        self.eip_status_changed = "status_changed"  # has parameter
        self.eip_state_changed = "state_changed"  # has parameter
        self.eip_process_finished = "process_finished"  # has parameter

    def get_noblock(self):
        s = None
        try:
            s = self._status.get(False)
        except Queue.Empty:
            pass

        return s

    def get(self):
        return self._status.get(timeout=1)

    def signal(self, status, data=None):
        self._status.put({'status': status, 'data': data})
