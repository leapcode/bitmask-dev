# -*- coding: utf-8 -*-
# management.py
# Copyright (c) 2012 Mike Mattice
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
Handles an OpenVPN process through its Management Interface.
"""

import time
from collections import OrderedDict

from twisted.protocols.basic import LineReceiver
from twisted.internet.defer import Deferred
from twisted.logger import Logger

from zope.interface import Interface

from _human import bytes2human


class IStateListener(Interface):

    def change_state(self, state):
        pass


class ManagementProtocol(LineReceiver):

    log = Logger()

    def __init__(self, verbose=False):

        self.verbose = verbose
        self.state = None
        self.remote = None
        self.rport = None
        self.traffic = TrafficCounter()
        self.openvpn_version = ''
        self.pid = None

        self._defs = []
        self._statelog = OrderedDict()
        self._linebuf = []
        self._state_listeners = set([])

    def addStateListener(self, listener):
        """
        A Listener must implement change_state method,
        and it will be called with a State object.
        """
        self._state_listeners.add(listener)

    # TODO -- this needs to be exposed by the API
    # The UI needs this feature.

    def getStateHistory(self):
        return self._statelog

    def lineReceived(self, line):
        if self.verbose:
            if int(self.verbose) > 1:
                print line
            elif line.startswith('>LOG'):
                print line

        if line[0] == '>':
            try:
                infotype, data = line[1:].split(':', 1)
                infotype = infotype.replace('-', '_')
            except Exception, msg:
                print "failed to parse '%r': %s" % (line, msg)
                raise
            m = getattr(self, '_handle_%s' % infotype, None)
            if m:
                try:
                    m(data)
                except Exception, msg:
                    print "Failure in _handle_%s: %s" % (infotype, msg)
            else:
                self._handle_unknown(infotype, data)
        else:
            if line.strip() == 'END':
                try:
                    d = self._defs.pop(0)
                    d.callback('\n'.join(self._linebuf))
                except IndexError:
                    pass
                self._linebuf = []
                return
            try:
                status, data = line.split(': ', 1)
            except ValueError:
                print "ERROR PARSING:", line
                return
            if status in ('ERROR', 'SUCCESS'):
                try:
                    d = self._defs.pop(0)
                    if status == 'SUCCESS':
                        d.callback(line)
                    else:
                        d.errback(line)
                except:
                    pass
            else:
                self._linebuf.append(line)

    def _handle_unknown(self, infotype, data):
        self.log.msg(
            'Received unhandled infotype %s with data %s' %
            (infotype, data))

    def _handle_BYTECOUNT(self, data):
        down, up = data.split(',')
        self.traffic.update(down, up, time.time())

    def _handle_ECHO(self, data):
        pass

    def _handle_FATAL(self, data):
        pass

    def _handle_HOLD(self, data):
        pass

    def _handle_INFO(self, data):
        pass

    def _handle_LOG(self, data):
        pass

    def _handle_NEED_OK(self, data):
        pass

    def _handle_NEED_STR(self, data):
        pass

    def _handle_STATE(self, data):
        data = data.strip().split(',')
        remote = rport = None
        state = ''
        ts = None
        try:
            if len(data) == 9:
                (ts, state, verbose, localtun,
                 remote, rport, laddr, lport, ip6) = data
            elif len(data) == 8:
                ts, state = data[:2]
            elif len(data) == 5:
                ts, state, verbose, localtun, remote = data
            else:
                raise ValueError(
                    'Cannot parse state data! %s' % data)
        except Exception as exc:
            self.log.error('Failure parsing data: %s' % exc)
            return

        if state != self.state:
            now = time.time()
            stateobj = State(state, ts)
            self._statelog[now] = stateobj
            for listener in self._state_listeners:
                listener.change_state(stateobj)
        self.state = stateobj
        self.remote = remote
        self.rport = rport

    def _pushdef(self):
        d = Deferred()
        self._defs.append(d)
        return d

    def byteCount(self, interval=0):
        d = self._pushdef()
        self.sendLine('bytecount %d' % (interval,))
        return d

    def signal(self, signal='SIGTERM'):
        d = self._pushdef()
        self.sendLine('signal %s' % (signal,))
        return d

    def _parseHoldstatus(self, result):
        return result.split('=')[0] == '1'

    def hold(self, p=''):
        d = self._pushdef()
        self.sendLine('hold %s' % (p,))
        if p == '':
            d.addCallback(self._parseHoldstatus)
        return d

    def _parsePid(self, result):
        self.pid = int(result.split('=')[1])

    def getPid(self):
        d = self._pushdef()
        self.sendLine('pid')
        d.addCallback(self._parsePid)
        return d

    def logOn(self):
        d = self._pushdef()
        self.sendLine('log on')
        return d

    def stateOn(self):
        d = self._pushdef()
        self.sendLine('state on')
        return d

    def _parseVersion(self, data):
        version = data.split('\n')[0].split(':')[1]
        self.openvpn_version = version.strip()

    def getVersion(self):
        d = self._pushdef()
        self.sendLine('version')
        d.addCallback(self._parseVersion)
        return d

    def getInfo(self):
        state = self._statelog.values()[-1]
        return {
            'remote': self.remote,
            'rport': self.rport,
            'state': state.state,
            'state_simple': state.simple,
            'state_legend': state.legend,
            'openvpn_version': self.openvpn_version,
            'pid': self.pid,
            'traffic_down_total': self.traffic.down,
            'traffic_up_total': self.traffic.up}


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
        'EXITING': 'A graceful exit is in progress'
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
        'EXITING': STOPPING
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


class TrafficCounter(object):

    CAPACITY = 60

    def __init__(self):
        self.down = None
        self.up = None
        self._buf = OrderedDict()

    def update(self, down, up, ts):
        i_down = int(down)
        i_up = int(up)
        self.down = i_down
        self.up = i_up
        if len(self._buf) > self.CAPACITY:
            self._buf.pop(self._buf.keys()[0])
        self._buf[ts] = i_down, i_up

    def get_rate(self, human=True):
        points = self._buf.items()
        if len(points) < 2:
            return ['NA', 'NA']
        ts1, prev = points[-2]
        ts2, last = points[-1]
        rate_down = _get_rate(last[0], prev[0], ts2, ts1)
        rate_up = _get_rate(last[1], prev[1], ts2, ts1)
        rates = rate_down, rate_up
        if human:
            rates = map(bytes2human, rates)
        return rates


def _get_rate(p2, p1, ts2, ts1):
    return ((1.0 * (p2 - p1)) / (ts2 - ts1))
