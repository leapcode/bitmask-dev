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

from time import strftime
from twisted.internet import defer

from leap.bitmask.hooks import HookableService
from leap.bitmask.vpn.vpn import VPNManager
from leap.bitmask.vpn._checks import is_service_ready, get_vpn_cert_path
from leap.bitmask.vpn import privilege, helpers
from leap.bitmask.vpn.privilege import NoPolkitAuthAgentAvailable
from leap.common.config import get_path_prefix
from leap.common.files import check_and_fix_urw_only
from leap.common.certs import get_cert_time_boundaries


class ImproperlyConfigured(Exception):
    """This error is a transient exception until autoconf automates all the
    needed steps for VPN bootstrap."""
    expected = True


class VPNService(HookableService):

    name = 'vpn'
    _last_vpn_path = os.path.join('leap', 'last_vpn')

    def __init__(self, basepath=None):
        """
        Initialize VPN service. This launches both the firewall and the vpn.
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
        if self._started:
            exc = Exception('VPN already started')
            exc.expected = True
            raise exc
        yield self._setup(domain)
        try:
            self._vpn.start()
        except NoPolkitAuthAgentAvailable as e:
            e.expected = True
            raise e

        self._started = True
        self._domain = domain
        self._write_last(domain)
        defer.returnValue({'result': 'started'})

    def stop_vpn(self):
        # TODO -----------------------------
        # when shutting down the main bitmaskd daemon, this should be called.

        if not self._vpn:
            raise Exception('VPN was not running')

        if self._started:
            self._vpn.stop()
            self._started = False
            return {'result': 'vpn stopped'}
        elif self._vpn.is_firewall_up():
            self._vpn.stop_firewall()
            return {'result': 'firewall stopped'}
        else:
            raise Exception('VPN was not running')

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

    def do_check(self, domain=None):
        """Check whether the VPN Service is properly configured,
        and can be started"""
        ret = {'installed': helpers.check()}
        if domain:
            ret['vpn_ready'] = is_service_ready(domain)
            ret['cert_expires'] = self._cert_expires(domain)
        return ret

    @defer.inlineCallbacks
    def do_get_cert(self, username):
        try:
            _, provider = username.split('@')
        except ValueError:
            if not username:
                raise ValueError('Need an username. are you logged in?')
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
        privilege.install_helpers()
        return {'install': 'ok'}

    def do_uninstall(self):
        privilege.uninstall_helpers()
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

        prefix = os.path.join(self._basepath, "leap", "providers", provider,
                              "keys")
        cert_path = key_path = os.path.join(prefix, "client", "openvpn.pem")
        ca_path = os.path.join(prefix, "ca", "cacert.pem")

        if not os.path.isfile(cert_path):
            raise ImproperlyConfigured(
                'Cannot find client certificate. Please get one')
        if not os.path.isfile(ca_path):
            raise ImproperlyConfigured(
                'Cannot find provider certificate. '
                'Please configure provider.')

        self._vpn = VPNManager(provider, remotes, cert_path, key_path, ca_path,
                               extra_flags)

    def _cert_expires(self, provider):
        path = os.path.join(self._basepath, "leap", "providers", provider,
                            "keys", "client", "openvpn.pem")
        with open(path, 'r') as f:
            cert = f.read()
        _, to = get_cert_time_boundaries(cert)
        return strftime('%Y-%m-%dT%H:%M:%SZ', to)

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
