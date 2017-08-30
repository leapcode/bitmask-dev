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
import copy
import time


def _normalized(label):
    return label.lower().replace(',', '_').replace(' ', '_')


class GatewaySelector(object):

    # http://www.timeanddate.com/time/map/
    equivalent_timezones = {13: -11, 14: -10}

    def __init__(self, gateways=None, locations=None, tz_offset=None,
                 preferred=None):
        '''
        Constructor for GatewaySelector.

        By default, we will use a Time Zone Heuristic to choose the closest
        gateway to the user.

        If the user specified something in the 'vpn_prefs' section of
        bitmaskd.cfg, we will passed a dictionary here with entries for
        'countries' and 'locations', in the form of a list. The 'locations'
        entry has preference over the 'countries' one.

        :param gateways: an unordered list of all the available gateways, read
                         from the eip-config file.
        :type gateways: list
        :param locations: a dictionary with the locations, as read from the
                          eip-config file
        :type locations: dict
        :param tz_offset: use this offset as a local distance to GMT.
        :type tz_offset: int
        :param preferred: a dictionary containing the country code (cc) and the
                          locations (locations) manually preferred by the user.
        :type preferred: dict
        '''
        if gateways is None:
            gateways = []
        if locations is None:
            locations = {}
        if preferred is None:
            preferred = {}
        self.gateways = gateways
        self.locations = locations
        self.preferred = preferred

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
        gateways = [gateway['ip_address']
                    for gateway in self.get_sorted_gateways()][:4]
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

            gateway = gateway.copy()
            if location is not None:
                gateway.update(location)
                timezone = location.get('timezone')
                if timezone is not None:
                    offset = int(timezone)
                    if offset in self.equivalent_timezones:
                        offset = self.equivalent_timezones[offset]
                    distance = self._get_timezone_distance(offset)
            gateway['distance'] = distance
            gateways_timezones.append(gateway)

        gateways_timezones = sorted(gateways_timezones,
                                    key=lambda gw: gw['distance'])
        return self.apply_user_preferences(gateways_timezones)

    def apply_user_preferences(self, options):
        """
        We re-sort the pre-sorted list of gateway options, according with the
        user's preferences.

        Location has preference over the Country Code indication.
        """
        applied = []
        presorted = copy.copy(options)
        for location in self.preferred.get('loc', []):
            for index, gw in enumerate(presorted):
                if ('location' in gw and
                        _normalized(gw['location']) == _normalized(location)):
                    applied.append(gw)
                    presorted.pop(index)

        for cc in self.preferred.get('cc', []):
            for index, gw in enumerate(presorted):
                if ('country_code' in gw and
                        _normalized(gw['country_code']) == _normalized(cc)):
                    applied.append(gw)
                    presorted.pop(index)
        if presorted:
            applied += presorted
        return applied

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
