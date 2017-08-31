# -*- coding: utf-8 -*-
# provider
# Copyright (C) 2017 LEAP
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
Bitmask Command Line interface: provider
"""
import argparse
import sys

from colorama import Fore

from leap.bitmask.cli import command


class Provider(command.Command):
    service = 'bonafide'
    usage = '''{name} provider <subcommand>

Bitmask bonafide provider service

SUBCOMMANDS:

   list       List providers
   read       Read provider
   delete     Delete the provider

'''.format(name=command.appname)

    def __init__(self, *args, **kwargs):
        super(Provider, self).__init__(*args, **kwargs)
        self.data.append('provider')

    def list(self, raw_args):
        self.data += ['list']
        return self._send(printer=self._print_domains)

    def read(self, raw_args):
        parser = argparse.ArgumentParser(
            description='Bitmask provider read',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('domain', nargs=1,
                            help='provider to gather info from')
        subargs = parser.parse_args(raw_args)

        self.data += ['read', subargs.domain[0]]
        return self._send(printer=command.default_printer)

    def delete(self, raw_args):
        parser = argparse.ArgumentParser(
            description='Bitmask provider delete',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('domain', nargs=1,
                            help='provider to delete')
        subargs = parser.parse_args(raw_args)

        self.data += ['delete', subargs.domain[0]]
        return self._send()

    def _print_domains(self, result):
        for i in result:
            print(Fore.GREEN + i['domain'] + Fore.RESET)
