# -*- coding: utf-8 -*-
# util.py
# Copyright (C) 2016 LEAP Encryption Acess Project
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
Handy common utils
"""
import os
import platform
import sys

from twisted.logger import Logger

from leap.common.files import which


STANDALONE = getattr(sys, 'frozen', False)

log = Logger()


def here(module=None):
    global STANDALONE

    if STANDALONE:
        # we are running in a |PyInstaller| bundle
        return sys._MEIPASS
    else:
        dirname = os.path.dirname
        if module:
            return dirname(module.__file__)
        else:
            return dirname(__file__)


def merge_status(children):

    def key(service):
        status = children[service]
        level = {
            "on": 0,
            "off": 1,
            "starting": 10,
            "stopping": 11,
            "failed": 100
        }
        return level.get(status["status"], -1)

    service = max(children, key=key)

    status = children[service]["status"]
    error = children[service]["error"]

    res = {}
    for s in children.values():
        res.update(s)
    res['status'] = status
    res['error'] = error
    res['childrenStatus'] = children
    return res


def get_gpg_bin_path():
    """
    Return the path to gpg binary.

    :returns: the gpg binary path
    :rtype: str
    """
    global STANDALONE
    if STANDALONE:
        if platform.system() == "Windows":
            gpgbin = os.path.abspath(
                os.path.join(here(), "apps", "mail", "gpg.exe"))
        elif platform.system() == "Darwin":
            gpgbin = os.path.abspath(
                os.path.join(here(), "apps", "mail", "gpg"))
        else:
            gpgbin = os.path.abspath(
                os.path.join(here(), "..", "apps", "mail", "gpg"))
        return gpgbin

    path_ext = '/bin:/usr/bin/:/usr/local/bin:/usr/local/opt/gnupg/bin/'
    for gpgbin_name in ["gpg1", "gpg"]:
        gpgbin_options = which(gpgbin_name, path_extension=path_ext)
        if len(gpgbin_options) >= 1:
            return gpgbin_options[0]

    log.debug("Could not find gpg binary")
    return None
