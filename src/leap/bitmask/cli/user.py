# -*- coding: utf-8 -*-
# user
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
Bitmask Command Line interface: user
"""
import argparse
import getpass
import sys
from copy import copy

from colorama import Fore
from twisted.internet import defer

from leap.bitmask.cli import command


class User(command.Command):
    service = 'bonafide'
    usage = '''{name} user <subcommand>

Bitmask account service

SUBCOMMANDS:

   create     Registers new user, if possible
   auth       Logs in against the provider
   logout     Ends any active session with the provider
   list       List users
   update     Update user password
   active     Shows the active user, if any

'''.format(name=command.appname)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.data.append('user')

    def create(self, raw_args):
        passwd = None

        for (index, item) in enumerate(raw_args):
            if item.startswith('--pass'):
                passwd = raw_args.pop(index + 1)
                raw_args.pop(index)

        parser = argparse.ArgumentParser(
            description='Bitmask user',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('--invitecode', **_invitecode_kw)
        parser.add_argument('username', **_username_kw)

        subargs = parser.parse_args(raw_args)

        # username parsing is factored out, but won't
        # accept the optional parameters. so strip them.
        args = copy(raw_args)
        for (index, item) in enumerate(args):
            if item.startswith('--'):
                args.pop(index + 1)
                args.pop(index)

        username = self._username(args, needed=True)
        if not passwd:
            passwd = self._getpass_twice()
        self.data += ['create', username, passwd,
                      subargs.invite, 'True']
        return self._send(printer=command.default_printer)

    def auth(self, raw_args):
        passwd = None
        for (index, item) in enumerate(raw_args):
            if item.startswith('--pass'):
                passwd = raw_args.pop(index + 1)
                raw_args.pop(index)

        username = self._username(raw_args, needed=True)
        if not passwd:
            passwd = getpass.getpass()
        self.data += ['authenticate', username, passwd, 'True']
        self.cfg.set('bonafide', 'active', username)
        return self._send(printer=command.default_printer)

    def logout(self, raw_args):
        username = self._username(raw_args)
        self.data += ['logout', username]

        active = self.cfg.get('bonafide', 'active', default=None)
        if active == username:
            self.cfg.set('bonafide', 'active', "")
        return self._send(printer=command.default_printer)

    def list(self, raw_args):
        self.data += ['list']
        return self._send(printer=self._print_user_list)

    def update(self, raw_args):
        username = self._username(raw_args)
        current_passwd = getpass.getpass('Current password: ')
        new_passwd = self._getpass_twice('New password: ')
        self.data += ['update', username, current_passwd, new_passwd]
        return self._send(printer=command.default_printer)

    def active(self, raw_args):
        username = self.cfg.get('bonafide', 'active', default='')
        if not username:
            username = '<none>'
        print(Fore.RESET + 'active'.ljust(10) + Fore.GREEN + username +
              Fore.RESET)
        return defer.succeed(None)

    def _username(self, raw_args, needed=False):
        parser = argparse.ArgumentParser(
            description='Bitmask user',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('username', **_username_kw)
        subargs = parser.parse_args(raw_args)

        username = subargs.username
        if not username:
            if needed:
                self._error("Missing username ID but needed for this command")
            else:
                return self.cfg.get('bonafide', 'active')
        if '@' not in username:
            self._error("Username ID must be in the form <user@example.org>")

        return username

    def _getpass_twice(self, prompt='Password: '):
        while True:
            passwd1 = getpass.getpass(prompt)
            passwd2 = getpass.getpass('Retype the password: ')
            if passwd1 == passwd2:
                return passwd1
            else:
                print "The passwords do not match, try again."
                print ""

    def _print_user_list(self, users):
        for u in users:
            color = ""
            if u['authenticated']:
                color = Fore.GREEN
            print(color + u['userid'] + Fore.RESET)


_username_kw = {
    'nargs': '?',
    'help': 'username ID, in the form <user@example.org>'}

_invitecode_kw = {
    'dest': 'invite',
    'default': 'none', 'action': 'store', 'nargs': '?', 'type': str,
    'help': 'invite code, if needed to register with this provider'}
