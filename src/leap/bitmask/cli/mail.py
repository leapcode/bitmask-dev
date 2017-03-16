# -*- coding: utf-8 -*-
# mail
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
Bitmask Command Line interface: mail
"""
import argparse
import sys

from colorama import Fore

from leap.bitmask.cli import command


class Mail(command.Command):
    service = 'mail'
    usage = '''{name} mail <subcommand>

Bitmask Encrypted Email Service

SUBCOMMANDS:

   enable               Start service
   disable              Stop service
   status               Display status about service
   get_token            Returns token for the mail service

'''.format(name=command.appname)

    commands = ['enable', 'disable', 'get_token']

    def status(self, raw_args):
        parser = argparse.ArgumentParser(
            description='Bitmask email status',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('uid', nargs='?', default=None,
                            help='uid to check the status of')
        subargs = parser.parse_args(raw_args)

        uid = None
        if subargs.uid:
            uid = subargs.uid
        else:
            uid = self.cfg.get('bonafide', 'active', default=None)
        self.data += ['status', uid]

        return self._send(command.print_status)
