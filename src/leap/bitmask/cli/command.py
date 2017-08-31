# -*- coding: utf-8 -*-
# sender
# Copyright (C) 2016 LEAP
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
Bitmask Command Line interface: zmq sender.
"""
import argparse
import json
import sys

from colorama import init as color_init
from colorama import Fore
from twisted.internet import defer
from txzmq import ZmqEndpoint, ZmqEndpointType
from txzmq import ZmqFactory, ZmqREQConnection
from txzmq import ZmqRequestTimeoutError

from leap.bitmask.core import ENDPOINT


appname = 'bitmaskctl'


def _print_result(result):
    print Fore.GREEN + '%s' % result + Fore.RESET


def default_printer(result, key=None):
    if isinstance(result, (str, unicode)):
        if result in ('OFF', 'OFFLINE', 'ABORTED', 'False'):
            color = Fore.RED
        else:
            color = Fore.GREEN

        print_str = ""
        if key is not None:
            print_str = Fore.RESET + key.ljust(10)
        print_str += color + result + Fore.RESET
        print(print_str)

    elif isinstance(result, list):
        if result and isinstance(result[0], list):
            result = map(lambda l: ' '.join(l), result)
            for item in result:
                default_printer('\t' + item, key)
        else:
            result = ' '.join(result)
            default_printer(result, key)

    elif isinstance(result, dict):
        for key, value in result.items():
            default_printer(value, key)

    else:
        default_printer(str(result), key)


def print_status(status, depth=0):

    if status.get('vpn') == 'disabled':
        print('vpn       ' + Fore.RED + 'disabled' + Fore.RESET)
        return

    for name, v in [('status', status)] + status['childrenStatus'].items():
        line = Fore.RESET + name.ljust(12)
        if v['status'] in ('on', 'starting'):
            line += Fore.GREEN
        elif v['status'] == 'failed':
            line += Fore.RED
        line += v['status']
        if v.get('error'):
            line += Fore.RED + " (%s)" % v['error']
        line += Fore.RESET
        print(line)

    for k, v in status.items():
        if k in ('status', 'childrenStatus', 'error'):
            continue
        if k == 'up':
            k = '↑↑↑         '
        elif k == 'down':
            k = '↓↓↓         '
        print(Fore.RESET + k.ljust(12) + Fore.CYAN + str(v) + Fore.RESET)


class Command(object):
    """A generic command dispatcher.
    Any command in the class attribute `commands` will be dispached and
    represented with a generic printer."""
    service = ''
    usage = '''{name} <subcommand>'''.format(name=appname)
    epilog = ("Use bitmaskctl <subcommand> --help' to learn more "
              "about each command.")
    commands = []

    def __init__(self, cfg, print_json=False):
        self.cfg = cfg

        color_init()
        zf = ZmqFactory()
        e = ZmqEndpoint(ZmqEndpointType.connect, ENDPOINT)
        self._conn = ZmqREQConnection(zf, e)

        self.data = []
        if self.service:
            self.data = [self.service]
        self.print_json = print_json

    def execute(self, raw_args):
        self.parser = argparse.ArgumentParser(usage=self.usage,
                                              epilog=self.epilog)
        self.parser.add_argument('command', help='Subcommand to run')
        try:
            args = self.parser.parse_args(raw_args[0:1])
        except SystemExit:
            return defer.succeed(None)

        # if command is in the default list, send the bare command
        # and use the default printer
        if args.command in self.commands:
            self.data += [args.command] + raw_args[1:]
            return self._send(printer=default_printer)

        elif (args.command == 'execute' or
                args.command.startswith('_') or
                not hasattr(self, args.command)):
            print 'Unrecognized command'
            return self.help([])

        try:
            # use dispatch pattern to invoke method with same name
            return getattr(self, args.command)(raw_args[1:])
        except SystemExit:
            return defer.succeed(None)

    def help(self, raw_args):
        self.parser.print_help()
        return defer.succeed(None)

    def _send(self, printer=_print_result, timeout=60, errb=None):
        d = self._conn.sendMsg(*self.data, timeout=timeout)
        d.addCallback(self._check_err, printer)
        d.addErrback(self._timeout_handler, errb)
        return d

    def _error(self, msg):
        print Fore.RED + "[!] %s" % msg + Fore.RESET
        sys.exit(1)

    def _check_err(self, stuff, printer):
        obj = json.loads(stuff[0])
        if self.print_json:
            print(json.dumps(obj, indent=2))
        elif not obj['error']:
            if 'result' not in obj:
                print (Fore.RED + 'ERROR: malformed response, expected'
                       ' obj["result"]' + Fore.RESET)
            elif obj['result'] is None:
                print (Fore.RED + 'ERROR: empty response. Check logs.' +
                       Fore.RESET)
            else:
                return printer(obj['result'])
        else:
            print Fore.RED + 'ERROR: ' + '%s' % obj['error'] + Fore.RESET

    def _timeout_handler(self, failure, errb):
        if failure.trap(ZmqRequestTimeoutError) == ZmqRequestTimeoutError:
            if callable(errb):
                errb()
            else:
                print (Fore.RED + "[ERROR] Timeout contacting the bitmask "
                       "daemon. Is it running?" + Fore.RESET)
