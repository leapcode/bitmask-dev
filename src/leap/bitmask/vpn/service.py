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
import json
import os

from twisted.internet import defer
from twisted.logger import Logger

from leap.bitmask.hooks import HookableService
from leap.bitmask.util import merge_status
from leap.bitmask.vpn.gateways import GatewaySelector
from leap.bitmask.vpn.fw.firewall import FirewallManager
from leap.bitmask.vpn.tunnel import ConfiguredTunnel
from leap.bitmask.vpn._checks import (
    is_service_ready,
    get_vpn_cert_path,
    cert_expires
)
from leap.bitmask.vpn import privilege, helpers
from leap.common.config import get_path_prefix
from leap.common.files import check_and_fix_urw_only


class ImproperlyConfigured(Exception):
    """This error is a transient exception until autoconf automates all the
    needed steps for VPN bootstrap."""
    expected = True


class VPNService(HookableService):

    name = 'vpn'
    _last_vpn_path = os.path.join('leap', 'last_vpn')
    log = Logger()

    def __init__(self, cfg, basepath=None):
        """
        Initialize VPN service. This launches both the firewall and the vpn.
        """
        super(VPNService, self).__init__()

        self._tunnel = None
        self._firewall = FirewallManager([])
        self._domain = ''
        self._cfg = cfg

        if basepath is None:
            self._basepath = get_path_prefix()
        else:
            self._basepath = basepath

        try:
            _cco = self._cfg.get('countries', "")
            self._cco = json.loads(_cco)
        except ValueError:
            self._cco = []
        try:
            _loc = self._cfg.get('locations', "")
            self._loc = json.loads(_loc)
        except ValueError:
            self._loc = []

        if helpers.check() and self._firewall.is_up():
            self._firewall.stop()

    def startService(self):
        # TODO this could trigger a check for validity of the certificates,
        # etc.
        super(VPNService, self).startService()

    def stopService(self):
        try:
            self.stop_vpn()
        except Exception as e:
            self.log.error('Error stopping vpn service... {0!r}'.format(e))
        super(VPNService, self).stopService()

    @defer.inlineCallbacks
    def start_vpn(self, domain=None):
        if self.do_status()['status'] == 'on':
            exc = Exception('VPN already started')
            exc.expected = True
            raise exc
        if not domain:
            domain = self._read_last()
            if not domain:
                exc = Exception("VPN can't start, a provider is needed")
                exc.expected = True
                raise exc
        if not is_service_ready(domain):
            exc = Exception("VPN is not ready")
            exc.expected = True
            raise exc

        yield self._setup(domain)

        fw_ok = self._firewall.start()
        if not fw_ok:
            raise Exception('Could not start firewall')

        try:
            result = yield self._tunnel.start()
        except Exception as exc:
            self._firewall.stop()
            # TODO get message from exception
            raise Exception('Could not start VPN (reason: %r)' % exc)

        self._domain = domain
        self._write_last(domain)
        if result is True:
            data = {'result': 'started'}
        else:
            data = {'result': 'failed', 'error': '%r' % result}

        defer.returnValue(data)

    def stop_vpn(self):
        if self._firewall.is_up():
            fw_ok = self._firewall.stop()
            if not fw_ok:
                self.log.error("Firewall: error stopping")

        if not self._tunnel:
            return {'result': 'VPN was not running'}

        vpn_ok = self._tunnel.stop()
        if not vpn_ok:
            raise Exception("Error stopping VPN")

        return {'result': 'vpn stopped'}

    def do_status(self):
        # TODO - add the current gateway and CC to the status
        childrenStatus = {
            'vpn': {'status': 'off', 'error': None},
            'firewall': {'status': 'off', 'error': None},
        }

        if self._tunnel:
            childrenStatus['vpn'] = self._tunnel.status
        childrenStatus['firewall'] = self._firewall.status
        status = merge_status(childrenStatus)

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
            expiry = cert_expires(domain).strftime('%Y-%m-%dT%H:%M:%SZ')
            ret['cert_expires'] = expiry
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
    def do_list(self):
        bonafide = self.parent.getServiceNamed("bonafide")
        _providers = yield bonafide.do_provider_list()
        providers = [p['domain'] for p in _providers]
        provider_dict = {}
        for provider in providers:
            try:
                config = yield bonafide.do_provider_read(provider, 'eip')
            except ValueError:
                continue
            gateways = GatewaySelector(
                config.gateways, config.locations,
                preferred={'cc': self._cco, 'loc': self._loc}
            )
            provider_dict[provider] = gateways.get_sorted_gateways()
        defer.returnValue(provider_dict)

    def do_set_locations(self, locations):
        self._loc = locations
        self._cfg.set('locations', json.dumps(locations))
        return {'locations': 'ok'}

    def do_get_locations(self):
        return self._loc

    def do_set_countries(self, countries):
        self._cco = countries
        self._cfg.set('countries', json.dumps(countries))
        return {'countries': 'ok'}

    def do_get_countries(self):
        return self._cco

    @defer.inlineCallbacks
    def _setup(self, provider):
        """Set up ConfiguredTunnel for a specified provider.

        :param provider: the provider to use, e.g. 'demo.bitmask.net'
        :type provider: str"""

        bonafide = self.parent.getServiceNamed('bonafide')
        config = yield bonafide.do_provider_read(provider, 'eip')

        sorted_gateways = GatewaySelector(
            config.gateways, config.locations,
            preferred={'cc': self._cco, 'loc': self._loc}
        ).select_gateways()

        extra_flags = config.openvpn_configuration

        prefix = os.path.join(
            self._basepath, "leap", "providers", provider, "keys")
        cert_path = key_path = os.path.join(prefix, "client", "openvpn.pem")
        ca_path = os.path.join(prefix, "ca", "cacert.pem")

        if not os.path.isfile(cert_path):
            raise ImproperlyConfigured(
                'Cannot find client certificate. Please get one')
        if not os.path.isfile(ca_path):
            raise ImproperlyConfigured(
                'Cannot find provider certificate. '
                'Please configure provider.')

        # TODO add remote ports, according to preferred sequence
        remotes = tuple([(ip, '443') for ip in sorted_gateways])
        self._tunnel = ConfiguredTunnel(
            provider, remotes, cert_path, key_path, ca_path, extra_flags)
        self._firewall = FirewallManager(remotes)

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
