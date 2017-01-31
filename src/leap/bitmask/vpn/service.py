#!/usr/bin/env python
# -*- coding: utf-8 -*-
# service.py
# Copyright (C) 2015-2017 LEAP
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
EIP service declaration.
"""

import os

from twisted.application import service
from twisted.python import log

from leap.bitmask.hooks import HookableService
from leap.bitmask.vpn import EIPManager
from leap.bitmask.vpn.utils import get_path_prefix


class EIPService(HookableService):

    def __init__(self, basepath=None):
        """
        Initialize EIP service
        """
        super(EIPService, self).__init__()

        self._started = False

        if basepath is None:
            self._basepath = get_path_prefix()
        else:
            self._basepath = basepath

    def _setup(self, provider):
        """
        Set up EIPManager for a specified provider.

        :param provider: the provider to use, e.g. 'demo.bitmask.net'
        :type provider: str
        """
        # FIXME
        # XXX picked manually from eip-service.json
        remotes = (
            ("198.252.153.84", "1194"),
            ("46.165.242.169", "1194"),
        )

        prefix = os.path.join(self._basepath,
                              "leap/providers/{0}/keys".format(provider))
        cert_path = key_path = prefix + "/client/openvpn.pem"
        ca_path = prefix + "/ca/cacert.pem"

        # FIXME
        # XXX picked manually from eip-service.json
        extra_flags = {
            "auth": "SHA1",
            "cipher": "AES-128-CBC",
            "keepalive": "10 30",
            "tls-cipher": "DHE-RSA-AES128-SHA",
            "tun-ipv6": "true",
        }

        self._eip = EIPManager(remotes, cert_path, key_path, ca_path,
                               extra_flags)

    def startService(self):
        print "Starting EIP Service..."
        super(EIPService, self).startService()

    def stopService(self):
        print "Stopping EIP Service..."
        super(EIPService, self).stopService()

    def do_start(self, domain):
        self._setup(domain)
        self._eip.start()
        self._started = True
        return "Starting"

    def do_stop(self):
        if self._started:
            self._eip.stop()
            self._started = False
            return "Stopping"
        else:
            return "Not started"
