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
VPN service declaration.
"""

import os

from twisted.internet import defer

from leap.bitmask.hooks import HookableService
from leap.bitmask.vpn.vpn import VPNManager
from leap.bitmask.vpn._checks import is_service_ready, get_vpn_cert_path
from leap.bitmask.vpn import privilege
from leap.common.config import get_path_prefix
from leap.common.files import check_and_fix_urw_only


class VPNService(HookableService):

    name = 'vpn'
    _last_vpn_path = os.path.join('leap', 'providers', 'last_vpn')

    def __init__(self, basepath=None):
        """
        Initialize VPN service
        """
        super(VPNService, self).__init__()

        self._started = False
        self._vpn = None
        self._domain = ''

        if basepath is None:
            self._basepath = get_path_prefix()
        else:
            self._basepath = basepath

    def startService(self):
        print "Starting VPN Service..."
        # TODO this could trigger a check for validity of the certificates,
        # etc.
        super(VPNService, self).startService()

    def stopService(self):
        print "Stopping VPN Service..."
        super(VPNService, self).stopService()

    @defer.inlineCallbacks
    def start_vpn(self, domain):
        # TODO check if the VPN is started and return an error if it is.
        yield self._setup(domain)
        self._vpn.start()
        self._started = True
        self._domain = domain
        self._write_last(domain)
        defer.returnValue({'result': 'started'})

    def stop_vpn(self):
        # TODO -----------------------------
        # when shutting down the main bitmaskd daemon, this should be called.

        if self._started:
            self._vpn.stop()
            self._started = False
            return {'result': 'stopped'}

    def do_status(self):
        status = {
            'status': 'off',
            'error': None,
            'childrenStatus': {}
        }
        if self._vpn:
            status = self._vpn.get_status()

        if self._domain:
            status['domain'] = self._domain
        else:
            status['domain'] = self._read_last()

        return status

    def do_check(self, domain):
        """Check whether the VPN Service is properly configured,
        and can be started"""
        return {'vpn_ready': is_service_ready(domain)}

    @defer.inlineCallbacks
    def do_get_cert(self, username):
        try:
            _, provider = username.split('@')
        except ValueError:
            raise ValueError(username + ' is not a valid username, it should'
                             ' contain an @')

        # fetch vpn cert and store
        bonafide = self.parent.getServiceNamed("bonafide")
        _, cert_str = yield bonafide.do_get_vpn_cert(username)

        cert_path = get_vpn_cert_path(provider)
        cert_dir = os.path.dirname(cert_path)
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir, mode=0700)
        with open(cert_path, 'w') as outf:
            outf.write(cert_str)
        check_and_fix_urw_only(cert_path)
        defer.returnValue({'get_cert': 'ok'})

    def do_install(self):
        ask = privilege.install_helpers()
        return {'install': 'ok'}

    def do_uninstall(self):
        ask = privilege.uninstall_helpers()
        return {'uninstall': 'ok'}

    @defer.inlineCallbacks
    def _setup(self, provider):
        """Set up VPNManager for a specified provider.

        :param provider: the provider to use, e.g. 'demo.bitmask.net'
        :type provider: str"""

        bonafide = self.parent.getServiceNamed("bonafide")
        config = yield bonafide.do_provider_read(provider, "eip")
        remotes = [(gw["ip_address"], gw["capabilities"]["ports"][0])
                   for gw in config.gateways]
        extra_flags = config.openvpn_configuration

        prefix = os.path.join(self._basepath,
                              "leap/providers/{0}/keys".format(provider))
        cert_path = key_path = prefix + "/client/openvpn.pem"
        ca_path = prefix + "/ca/cacert.pem"

        self._vpn = VPNManager(provider, remotes, cert_path, key_path, ca_path,
                               extra_flags)

    def _write_last(self, domain):
        path = os.path.join(self._basepath, self._last_vpn_path)
        with open(path, 'w') as f:
            f.write(domain)

    def _read_last(self):
        path = os.path.join(self._basepath, self._last_vpn_path)
        try:
            with open(path, 'r') as f:
                domain = f.read()
        except IOError:
            domain = None
        return domain
