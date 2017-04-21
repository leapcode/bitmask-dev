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

from leap.bitmask.util import merge_status
from leap.bitmask.vpn.manager import TunnelManager
from leap.bitmask.vpn.fw.firewall import FirewallManager


class VPNManager(object):

    def __init__(self, provider, remotes, cert, key, ca, flags):

        self._vpn = TunnelManager(
            provider, remotes, cert, key, ca, flags)
        self._firewall = FirewallManager(remotes)
        self.starting = False

    def start(self):
        # TODO we should have some way of switching this flag to False
        # other than parsing the result of the status command.
        self.starting = True
        print(Fore.BLUE + "Firewall: starting..." + Fore.RESET)
        fw_ok = self._firewall.start()
        if not fw_ok:
            print(Fore.RED + "Firewall: problem!")
            self.starting = False
            return False
        print(Fore.GREEN + "Firewall: started" + Fore.RESET)

        vpn_ok = self._vpn.start()
        if not vpn_ok:
            print (Fore.RED + "VPN: Error starting." + Fore.RESET)
            self._firewall.stop()
            print(Fore.GREEN + "Firewall: stopped." + Fore.RESET)
            self.starting = False
            return False
        print(Fore.GREEN + "VPN: started" + Fore.RESET)

    def stop(self):
        self.starting = False
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

    def stop_firewall(self):
        self._firewall.stop()

    def is_firewall_up(self):
        return self._firewall.is_up()

    def get_status(self):
        childrenStatus = {
            "vpn": self._vpn.status,
            "firewall": self._firewall.status
        }
        if self.starting:
            # XXX small correction to the merge: if we are starting fw+vpn,
            # we report vpn as starting so that is consistent with the ui or
            # cli action. this state propagates from the parent
            # object to the vpn child, and we revert it when we reach
            # the 'on' state. this needs to be revisited in the formal state
            # machine, and mainly needs a way of setting that state directly
            # and resetting the 'starting' flag without resorting to hijack
            # this command.
            vpnstatus = childrenStatus['vpn']['status']
            if vpnstatus == 'off':
                childrenStatus['vpn']['status'] = 'starting'
            if vpnstatus == 'on':
                self.starting = False
        return merge_status(childrenStatus)
