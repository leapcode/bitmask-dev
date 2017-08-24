# -*- coding: utf-8 -*-
# configurable.py
# Copyright (C) 2015, 2016 LEAP
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
Configurable Backend for Bitmask Service.
"""
from twisted.application import service

from leap.bitmask.config import (
    Configuration,
    DEFAULT_BASEDIR,
    MissingConfigEntry
)


class ConfigurableService(service.MultiService):

    config_file = u"bitmaskd.cfg"
    service_names = ('mail', 'vpn', 'zmq', 'web', 'websockets')

    def __init__(self, basedir=DEFAULT_BASEDIR):
        service.MultiService.__init__(self)
        self.cfg = Configuration(self.config_file, basedir, DEFAULT_CONFIG)
        self.basedir = basedir

    def get_config(self, section, option, default=None, boolean=False):
        return self.cfg.get(section, option, default=default, boolean=boolean)

    def set_config(self, section, option, value):
        return self.cfg.set(section, option, value)

    def get_config_section(self, section):
        return self.cfg.get_section(section)


DEFAULT_CONFIG = """[services]
mail = True
vpn = True
zmq = True
web = True
onion = False
websockets = False
mixnet = False
"""

__all__ = ["ConfigurableService", DEFAULT_BASEDIR, MissingConfigEntry]
