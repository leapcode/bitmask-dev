# -*- coding: utf-8 -*-
# config.py
# Copyright (C) 2017 LEAP
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
Configuration parser/writter
"""
import ConfigParser
import os

from leap.common import files
from leap.common.config import get_path_prefix


DEFAULT_BASEDIR = os.path.join(get_path_prefix(), 'leap')


class MissingConfigEntry(Exception):
    """
    A required config entry was not found.
    """


class Configuration(object):

    def __init__(self, config_file, basedir=DEFAULT_BASEDIR,
                 default_config=""):
        path = os.path.abspath(os.path.expanduser(basedir))
        if not os.path.isdir(path):
            files.mkdir_p(path)
        self.config_path = os.path.join(path, config_file)
        self.default_config = default_config

        self.read()

    def get(self, section, option, default=None, boolean=False):
        try:
            if boolean:
                return self.config.getboolean(section, option)

            item = self.config.get(section, option)
            return item

        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            if default is None:
                raise MissingConfigEntry("%s is missing the [%s]%s entry"
                                         % (self.config_path, section, option))
            return default

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        self.save()
        self.read()
        assert self.config.get(section, option) == value

    def get_section(self, section):
        return _ConfigurationSection(self, section)

    def read(self):
        self.config = ConfigParser.SafeConfigParser()
        if not os.path.isfile(self.config_path):
            self._create_default_config()

        with open(self.config_path, "rb") as f:
            self.config.readfp(f)

    def save(self):
        with open(self.config_path, 'wb') as f:
            self.config.write(f)

    def _create_default_config(self):
        with open(self.config_path, 'w') as outf:
            outf.write(self.default_config)


class _ConfigurationSection(object):
    def __init__(self, config, section):
        self.config = config
        self.section = section

    def get(self, option, default=None, boolean=False):
        return self.config.get(self.section, option, default, boolean)

    def set(self, option, value):
        return self.config.set(self.section, option, value)
