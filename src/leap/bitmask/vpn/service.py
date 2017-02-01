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

from twisted.internet import defer

from leap.bitmask.hooks import HookableService
from leap.bitmask.vpn.eip import EIPManager
from leap.bitmask.vpn._checks import is_service_ready, get_eip_cert_path
from leap.common.config import get_path_prefix
from leap.common.files import check_and_fix_urw_only


class EIPService(HookableService):

    name = 'eip'

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

    def startService(self):
        print "Starting EIP Service..."
        # TODO this could trigger a check for validity of the certificates,
        # etc.
        super(EIPService, self).startService()

    def stopService(self):
        print "Stopping EIP Service..."
        super(EIPService, self).stopService()

    def start_vpn(self, domain):
        self._setup(domain)
        self._eip.start()
        self._started = True
        return "Starting"

    def stop_vpn(self):
        if self._started:
            self._eip.stop()
            self._started = False
            return "Stopping"
        else:
            return "Not started"

    def do_status(self):
        # TODO -- get status from a dedicated STATUS CLASS
        return {'result': 'running'}

    def do_check(self):
        """Check whether the EIP Service is properly configured,
        and can be started"""
        # TODO either pass a provider, or set a given provider
        _ready = is_service_ready('demo.bitmask.net')
        return {'eip_ready': 'ok'}

    @defer.inlineCallbacks
    def do_get_cert(self, provider):
        # fetch vpn cert and store
        bonafide = self.parent.getServiceNamed("bonafide")
        _, cert_str = yield bonafide.do_get_vpn_cert()

        cert_path = get_eip_cert_path(provider)
        cert_dir = os.path.dirname(cert_path)
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir, mode=0700)
        with open(cert_path, 'w') as outf:
            outf.write(cert_str)
        check_and_fix_urw_only(cert_path)
        defer.returnValue({'get_cert': 'ok'})

    def _setup(self, provider):
        """Set up EIPManager for a specified provider.

        :param provider: the provider to use, e.g. 'demo.bitmask.net'
        :type provider: str"""
        # FIXME
        # XXX picked manually from eip-service.json
        remotes = (
            ("198.252.153.84", "1194 "),
            ("46.165.242.169", "1194 "),
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
