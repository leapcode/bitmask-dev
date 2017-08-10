# -*- coding: utf-8 -*-
# gateways.py
# Copyright (C) 2013-2017 LEAP Encryption Access Project
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
Gateway Selection
"""

import logging
import os
import re
import time

from leap.common.config import get_path_prefix


class GatewaySelector(object):

    # http://www.timeanddate.com/time/map/
    equivalent_timezones = {13: -11, 14: -10}

    def __init__(self, gateways=None, locations=None, tz_offset=None):
        '''
        Constructor for GatewaySelector.

        :param tz_offset: use this offset as a local distance to GMT.
        :type tz_offset: int
        '''
        if gateways is None:
            gateways = []
        if locations is None:
            locations = {}
        self.gateways = gateways
        self.locations = locations
        self._local_offset = tz_offset
        if tz_offset is None:
            tz_offset = self._get_local_offset()
        if tz_offset in self.equivalent_timezones:
            tz_offset = self.equivalent_timezones[tz_offset]
        self._local_offset = tz_offset

    def select_gateways(self):
        """
        Returns the IPs top 4 preferred gateways, in order.
        """
        gateways = [gateway[1] for gateway in self.get_sorted_gateways()][:4]
        return gateways

    def get_sorted_gateways(self):
        """
        Returns a tuple with location-label, IP and Country Code with all the
        available gateways, sorted by order of preference.
        """
        gateways_timezones = []
        locations = self.locations

        for idx, gateway in enumerate(self.gateways):
            distance = 99  # if hasn't location -> should go last
            location = locations.get(gateway.get('location'))

            label = gateway.get('location', 'Unknown')
            country = 'XX'
            if location is not None:
                country = location.get('country_code', 'XX')
                label = location.get('name', label)
                timezone = location.get('timezone')
                if timezone is not None:
                    offset = int(timezone)
                    if offset in self.equivalent_timezones:
                        offset = self.equivalent_timezones[offset]
                    distance = self._get_timezone_distance(offset)
            ip = self.gateways[idx].get('ip_address')
            gateways_timezones.append((ip, distance, label, country))

        gateways_timezones = sorted(gateways_timezones, key=lambda gw: gw[1])

        result = []
        for ip, distance, label, country in gateways_timezones:
            result.append((label, ip, country))
        return result

    def get_gateways_country_code(self):
        country_codes = {}
        locations = self.locations
        if not locations:
            return
        gateways = self.gateways

        for idx, gateway in enumerate(gateways):
            gateway_location = gateway.get('location')

            ip = self._eipconfig.get_gateway_ip(idx)
            if gateway_location is not None:
                ccode = locations[gateway['location']]['country_code']
                country_codes[ip] = ccode
        return country_codes

    def _get_timezone_distance(self, offset):
        '''
        Return the distance between the local timezone and
        the one with offset 'offset'.

        :param offset: the distance of a timezone to GMT.
        :type offset: int
        :returns: distance between local offset and param offset.
        :rtype: int
        '''
        timezones = range(-11, 13)
        tz1 = offset
        tz2 = self._local_offset
        distance = abs(timezones.index(tz1) - timezones.index(tz2))
        if distance > 12:
            if tz1 < 0:
                distance = timezones.index(tz1) + timezones[::-1].index(tz2)
            else:
                distance = timezones[::-1].index(tz1) + timezones.index(tz2)

        return distance

    def _get_local_offset(self):
        '''
        Return the distance between GMT and the local timezone.

        :rtype: int
        '''
        local_offset = time.timezone
        if time.daylight:
            local_offset = time.altzone

        return -local_offset / 3600
