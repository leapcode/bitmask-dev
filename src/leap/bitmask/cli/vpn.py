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
   get_cert   Get VPN Certificate from provider
   install    Install helpers (needs root)
   uninstall  Uninstall helpers (needs root)

'''.format(name=command.appname)

    commands = ['start', 'stop', 'status', 'check',
                'get_cert', 'install', 'uninstall',
                'enable', 'disable']
