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
   add_msg              Add a msg file to a mailbox

'''.format(name=command.appname)

    commands = ['enable', 'disable']

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

    def get_token(self, raw_args):
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
        self.data += ['get_token', uid]

        return self._send(command.default_printer)

    def add_msg(self, raw_args):
        parser = argparse.ArgumentParser(
            description='Bitmask email status',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('-u', '--userid', default='',
                            help='Select the userid of the mail')
        parser.add_argument('-m', '--mailbox', default='',
                            help='Select the mailbox to add the email')
        parser.add_argument('file', nargs=1,
                            help='file where the mail is stored')
        subargs = parser.parse_args(raw_args)

        if subargs.userid:
            userid = subargs.userid
        else:
            userid = self.cfg.get('bonafide', 'active', default=None)

        mailbox = ''
        if subargs.mailbox:
            mailbox = subargs.mailbox

        with open(subargs.file[0], 'r') as msgfile:
            rawmsg = msgfile.read()

        self.data += ['add_msg', userid, mailbox, rawmsg]

        return self._send(command.default_printer)

    def mixnet_status(self, raw_args):
        parser = argparse.ArgumentParser(
            description='Bitmask mixnet status',
            prog='%s %s %s' % tuple(sys.argv[:3]))
        parser.add_argument('-u', '--userid', default='',
                            help='uid to check the status of')
        parser.add_argument('address', nargs=1,
                            help='the recipient address')
        subargs = parser.parse_args(raw_args)

        userid = None
        if subargs.userid:
            userid = subargs.userid
        else:
            userid = self.cfg.get('bonafide', 'active', default=None)
        self.data += ['mixnet_status', userid, subargs.address[0]]

        return self._send(command.default_printer)
