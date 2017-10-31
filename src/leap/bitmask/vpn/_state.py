# -*- coding: utf-8 -*-
# _state.py
# Copyright (C) 2017 LEAP Encryption Access Project
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
VPN State.
"""

import time


class State(object):

    """
    Possible States in an OpenVPN connection, according to the
    OpenVPN Management documentation.
    """

    CONNECTING = 'CONNECTING'
    WAIT = 'WAIT'
    AUTH = 'AUTH'
    GET_CONFIG = 'GET_CONFIG'
    ASSIGN_IP = 'ASSIGN_IP'
    ADD_ROUTES = 'ADD_ROUTES'
    CONNECTED = 'CONNECTED'
    RECONNECTING = 'RECONNECTING'
    EXITING = 'EXITING'

    OFF = 'OFF'
    ON = 'ON'
    STARTING = 'STARTING'
    STOPPING = 'STOPPING'
    FAILED = 'FAILED'

    _legend = {
        'CONNECTING': 'Connecting to remote server',
        'WAIT': 'Waiting from initial response from server',
        'AUTH': 'Authenticating with server',
        'GET_CONFIG': 'Downloading configuration options from server',
        'ASSIGN_IP': 'Assigning IP address to virtual network interface',
        'ADD_ROUTES': 'Adding routes to system',
        'CONNECTED': 'Initialization Sequence Completed',
        'RECONNECTING': 'A restart has occurred',
        'EXITING': 'A graceful exit is in progress',
        'OFF': 'Disconnected',
        'FAILED': 'A failure has occurred',
    }

    _simple = {
        'CONNECTING': STARTING,
        'WAIT': STARTING,
        'AUTH': STARTING,
        'GET_CONFIG': STARTING,
        'ASSIGN_IP': STARTING,
        'ADD_ROUTES': STARTING,
        'CONNECTED': ON,
        'RECONNECTING': STARTING,
        'EXITING': STOPPING,
        'OFF': OFF,
        'FAILED': OFF
    }

    def __init__(self, state, timestamp):
        self.state = state
        self.timestamp = timestamp

    @classmethod
    def get_legend(cls, state):
        return cls._legend.get(state)

    @classmethod
    def get_simple(cls, state):
        return cls._simple.get(state)

    @property
    def simple(self):
        return self.get_simple(self.state)

    @property
    def legend(self):
        return self.get_legend(self.state)

    def __repr__(self):
        return '<State: %s [%s]>' % (
            self.state, time.ctime(int(self.timestamp)))
