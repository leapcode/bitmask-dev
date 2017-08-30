# -*- coding: utf-8 -*-
# test_gateways.py
# Copyright (C) 2017 LEAP Encryption Access Project
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
tests for leap.bitmask.vpn.gateways
"""
import time

from twisted.trial import unittest

from leap.bitmask.vpn.gateways import GatewaySelector


sample_gateways = [
    {u'host': u'gateway1.com',
     u'ip_address': u'1.2.3.4',
     u'location': u'location1'},
    {u'host': u'gateway2.com',
     u'ip_address': u'2.3.4.5',
     u'location': u'location2'},
    {u'host': u'gateway3.com',
     u'ip_address': u'3.4.5.6',
     u'location': u'location3'},
    {u'host': u'gateway4.com',
     u'ip_address': u'4.5.6.7',
     u'location': u'location4'}
]

sample_gateways_no_location = [
    {u'host': u'gateway1.com',
     u'ip_address': u'1.2.3.4'},
    {u'host': u'gateway2.com',
     u'ip_address': u'2.3.4.5'},
    {u'host': u'gateway3.com',
     u'ip_address': u'3.4.5.6'}
]

sample_locations = {
    u'location1': {u'timezone': u'2'},
    u'location2': {u'timezone': u'-7'},
    u'location3': {u'timezone': u'-4'},
    u'location4': {u'timezone': u'+13'}
}

# 0 is not used, only for indexing from 1 in tests
ips = (0, u'1.2.3.4', u'2.3.4.5', u'3.4.5.6', u'4.5.6.7')


class GatewaySelectorTestCase(unittest.TestCase):

    def test_get_no_gateways(self):
        selector = GatewaySelector()
        gateways = selector.select_gateways()
        assert gateways == []

    def test_get_gateway_with_no_locations(self):
        selector = GatewaySelector(
            gateways=sample_gateways_no_location)
        gateways = selector.select_gateways()
        gateways_default_order = [
            sample_gateways[0]['ip_address'],
            sample_gateways[1]['ip_address'],
            sample_gateways[2]['ip_address']
        ]
        assert gateways == gateways_default_order

    def test_correct_order_gmt(self):
        selector = GatewaySelector(
            sample_gateways, sample_locations,
            tz_offset=0)
        gateways = selector.select_gateways()
        assert gateways == [ips[1], ips[3], ips[2], ips[4]]

    def test_correct_order_gmt_minus_3(self):
        selector = GatewaySelector(
            sample_gateways, sample_locations,
            tz_offset=-3)
        gateways = selector.select_gateways()
        assert gateways == [ips[3], ips[2], ips[1], ips[4]]

    def test_correct_order_gmt_minus_7(self):
        selector = GatewaySelector(
            sample_gateways, sample_locations,
            tz_offset=-7)
        gateways = selector.select_gateways()
        assert gateways == [ips[2], ips[3], ips[4], ips[1]]

    def test_correct_order_gmt_plus_5(self):
        selector = GatewaySelector(
            sample_gateways, sample_locations,
            tz_offset=5)
        gateways = selector.select_gateways()
        assert gateways == [ips[1], ips[4], ips[3], ips[2]]

    def test_correct_order_gmt_plus_12(self):
        selector = GatewaySelector(
            sample_gateways, sample_locations,
            tz_offset=12)
        gateways = selector.select_gateways()
        assert gateways == [ips[4], ips[2], ips[3], ips[1]]

    def test_correct_order_gmt_minus_11(self):
        selector = GatewaySelector(
            sample_gateways, sample_locations,
            -11)
        gateways = selector.select_gateways()
        assert gateways == [ips[4], ips[2], ips[3], ips[1]]

    def test_correct_order_gmt_plus_14(self):
        selector = GatewaySelector(
            sample_gateways, sample_locations,
            14)
        gateways = selector.select_gateways()
        assert gateways == [ips[4], ips[2], ips[3], ips[1]]

    def test_apply_user_preferences(self):
        def to_gateways(gws):
            return [{'location': x[0], 'ip_address': x[1],
                     'country_code': x[2]}
                    for x in gws]

        preferred = {
            'loc': ['anarres', 'paris__fr', 'montevideo'],
            'cc': ['BR', 'AR', 'UY'],
        }
        selector = GatewaySelector(preferred=preferred)
        pre = [
            ('Seattle', '1.1.1.1', 'US'),
            ('Rio de Janeiro', '1.1.1.1', 'BR'),
            ('Montevideo', '1.1.1.1', 'UY'),
            ('Cordoba', '1.1.1.1', 'AR')]
        ordered = selector.apply_user_preferences(to_gateways(pre))
        locations = [x['location'] for x in ordered]
        # first the preferred location, then order by country
        assert locations == [
            'Montevideo',
            'Rio de Janeiro',
            'Cordoba',
            'Seattle']

        pre = [
            ('Seattle', '', ''),
            ('Montevideo', '', ''),
            ('Paris, FR', '', ''),
            ('AnaRreS', '', '')]
        ordered = selector.apply_user_preferences(to_gateways(pre))
        locations = [x['location'] for x in ordered]
        # first the preferred location, then order by country
        # (test normalization)
        assert locations == [
            'AnaRreS',
            'Paris, FR',
            'Montevideo',
            'Seattle']

        pre = [
            ('Rio De Janeiro', '', 'BR'),
            ('Tacuarembo', '', 'UY'),
            ('Sao Paulo', '', 'BR'),
            ('Cordoba', '', 'AR')]
        ordered = selector.apply_user_preferences(to_gateways(pre))
        locations = [x['location'] for x in ordered]
        # no matching location, order by country
        assert locations == [
            'Rio De Janeiro',
            'Sao Paulo',
            'Cordoba',
            'Tacuarembo']
