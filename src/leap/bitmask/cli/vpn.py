# -*- coding: utf-8 -*-
# vpn
# Copyright (C) 2016-2017 LEAP
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
Bitmask Command Line interface: vpn module
"""
import argparse
import sys

from colorama import Fore

from leap.bitmask.cli import command


class VPN(command.Command):
    service = 'vpn'
    usage = '''{name} vpn <subcommand>

Bitmask VPN Service

SUBCOMMANDS:

   enable     Enable VPN Service
   disable    Disable VPN Service
   start      Start VPN
   stop       Stop VPN
   status     Display status about the VPN
   check      Check whether VPN service is properly configured
   list       List the configured gateways
   get_cert   Get VPN Certificate from provider
   install    Install helpers (needs root)
   uninstall  Uninstall helpers (needs root)

'''.format(name=command.appname)

    commands = ['stop', 'install', 'uninstall',
                'enable', 'disable', 'locations', 'countries']

    def start(self, raw_args):
        parser = argparse.ArgumentParser(
            description='Bitmask VPN start',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('provider', nargs='?', default=None,
                            help='provider to start the VPN')
        subargs = parser.parse_args(raw_args)

        provider = ""
        if subargs.provider:
            provider = subargs.provider
        else:
            uid = self.cfg.get('bonafide', 'active', default=None)
            try:
                _, provider = uid.split('@')
            except ValueError:
                pass

        self.data += ['start', provider]

        return self._send(command.default_printer)

    def status(self, raw_args):
        self.data += ['status']
        return self._send(command.print_status)

    def check(self, raw_args):
        parser = argparse.ArgumentParser(
            description='Bitmask VPN check',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('provider', nargs='?', default=None,
                            help='provider to check the VPN')
        subargs = parser.parse_args(raw_args)

        provider = ""
        if subargs.provider:
            provider = subargs.provider
        else:
            uid = self.cfg.get('bonafide', 'active', default=None)
            try:
                _, provider = uid.split('@')
            except ValueError:
                pass

        self.data += ['check', provider]

        return self._send(command.default_printer)

    def list(self, raw_args):
        self.data += ['list']
        return self._send(location_printer)

    def get_cert(self, raw_args):
        parser = argparse.ArgumentParser(
            description='Bitmask VPN cert fetcher',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('uid', nargs='?', default=None,
                            help='uid to fetch the VPN cert')
        subargs = parser.parse_args(raw_args)

        uid = None
        if subargs.uid:
            uid = subargs.uid
        else:
            uid = self.cfg.get('bonafide', 'active', default=None)
        self.data += ['get_cert', uid]

        return self._send(command.default_printer)


def location_printer(result):
    def pprint(key, value):
        print(Fore.RESET + key.ljust(20) + Fore.GREEN +
              value + Fore.RESET)

    for provider, locations in result.items():
        for loc in locations:
            if 'name' not in loc:
                pprint(provider, "---")
            else:
                location_str = ("[%(country_code)s] %(name)s "
                                "(UTC%(timezone)s %(hemisphere)s)" % loc)
                pprint(provider, location_str)
