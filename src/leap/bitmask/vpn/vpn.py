#!/usr/bin/env python
# -*- coding: utf-8 -*-
# cli.py
# Copyright (C) 2015 LEAP
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

from colorama import Fore

from leap.bitmask.vpn.manager import TunnelManager
from leap.bitmask.vpn.fw.firewall import FirewallManager


class VPNManager(object):

    def __init__(self, remotes, cert, key, ca, flags):

        self._vpn = TunnelManager(
            remotes, cert, key, ca, flags)
        self._firewall = FirewallManager(remotes)

    def start(self):
        print(Fore.BLUE + "Firewall: starting..." + Fore.RESET)
        fw_ok = self._firewall.start()
        if not fw_ok:
            print(Fore.RED + "Firewall: problem!")
            return False

        print(Fore.GREEN + "Firewall: started" + Fore.RESET)

        vpn_ok = self._vpn.start()
        if not vpn_ok:
            print (Fore.RED + "VPN: Error starting." + Fore.RESET)
            self._firewall.stop()
            print(Fore.GREEN + "Firewall: stopped." + Fore.RESET)
            return False

        print(Fore.GREEN + "VPN: started" + Fore.RESET)

    def stop(self):
        print(Fore.BLUE + "Firewall: stopping..." + Fore.RESET)
        fw_ok = self._firewall.stop()

        if not fw_ok:
            print (Fore.RED + "Firewall: Error stopping." + Fore.RESET)
            return False

        print(Fore.GREEN + "Firewall: stopped." + Fore.RESET)
        print(Fore.BLUE + "VPN: stopping..." + Fore.RESET)

        vpn_ok = self._vpn.stop()
        if not vpn_ok:
            print (Fore.RED + "VPN: Error stopping." + Fore.RESET)
            return False

        print(Fore.GREEN + "VPN: stopped." + Fore.RESET)
        return True

    def get_status(self):
        vpn_status = self._vpn.status
        # TODO use firewall.is_up instead
        fw_status = self._firewall.status

        result = {'VPN': vpn_status,
                  'firewall': fw_status}
        if vpn_status == 'CONNECTED':
            traffic = self._vpn.traffic_status
            result['↑↑↑'] = traffic['up']
            result['↓↓↓'] = traffic['down']
        return result
