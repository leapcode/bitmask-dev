# -*- coding: utf-8 -*-
# test_management.py
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
Tests for the VPN Management Interface
"""

import StringIO

from twisted.trial import unittest
from leap.bitmask.vpn.management import ManagementProtocol


session1 = open('session1.data').readlines()
session2 = open('session2.data').readlines()


def feed_the_protocol(protocol, data):
    for line in data:
        protocol.lineReceived(line)


class StateListener(object):

    def __init__(self):
        self.states = []

    def change_state(self, state):
        self.states.append(state)


class ManagementTestCase(unittest.TestCase):

    def test_final_state_is_connected(self):
        proto = ManagementProtocol()
        feed_the_protocol(proto, session1)
        assert proto.state.state == 'CONNECTED'
        assert proto.state.simple == 'ON'
        assert proto.remote == '46.165.242.169'

    def test_final_state_stopping(self):
        proto = ManagementProtocol()
        feed_the_protocol(proto, session2)
        assert proto.state.state == 'EXITING'
        assert proto.state.simple == 'STOPPING'

    def test_get_state_history(self):
        proto = ManagementProtocol()
        feed_the_protocol(proto, session1)
        log = proto.getStateHistory()
        states = [st.state for st in log.values()]
        assert len(log) == 4
        assert states == ['AUTH', 'GET_CONFIG', 'ASSIGN_IP', 'CONNECTED']

    def test_state_listener(self):
        proto = ManagementProtocol()
        listener = StateListener()
        proto.addStateListener(listener)
        feed_the_protocol(proto, session1)
        states = [st.state for st in listener.states]
        assert states == ['AUTH', 'GET_CONFIG', 'ASSIGN_IP', 'CONNECTED']

    def test_bytecount(self):
        proto = ManagementProtocol()
        feed_the_protocol(proto, session1)
        assert proto.traffic.down == 17168
        assert proto.traffic.up == 7657

    def test_bytecount_rate(self):
        proto = ManagementProtocol()
        proto.traffic.update(1024, 512, 1)
        proto.traffic.update(2048, 1024, 2)
        print proto.traffic._buf
        assert proto.traffic.down == 2048
        assert proto.traffic.up == 1024
        assert proto.traffic.get_rate() == ['1.0 K', '512.0 B']

    def test_get_pid(self):
        proto = ManagementProtocol()
        proto.transport = StringIO.StringIO()
        assert proto.pid == None
        proto.getPid()
        pid_lines = ['SUCCESS: pid=99999']
        feed_the_protocol(proto, pid_lines)
        assert proto.pid == 99999

    def test_parse_version_string(self):
        proto = ManagementProtocol()
        proto.transport = StringIO.StringIO()
        assert proto.openvpn_version == ''
        feed_the_protocol(proto, session1[2:4])
        proto.getVersion()
        feed_the_protocol(proto, ['END'])
        assert proto.openvpn_version.startswith('OpenVPN 2.4.0')

    def test_get_info(self):
        proto = ManagementProtocol()
        proto.transport = StringIO.StringIO()
        feed_the_protocol(proto, session1)

        feed_the_protocol(proto, session1[2:4])
        proto.getVersion()
        feed_the_protocol(proto, ['END'])
        proto.get_pid()
        pid_lines = ['SUCCESS: pid=23783']
        feed_the_protocol(proto, pid_lines)

        info = proto.getInfo()
        assert info['remote'] == '46.165.242.169'
        assert info['rport'] == '443'
        assert info['state'] == 'CONNECTED'
        assert info['state_simple'] == 'ON'
        assert info['state_legend'] == 'Initialization Sequence Completed'
        assert info['openvpn_version'].startswith('OpenVPN 2.4.0')
        assert info['pid'] == 23783 
