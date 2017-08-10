# -*- coding: utf-8 -*-
# chrome-app.py
# Copyright (C) 2017 LEAP Encryption Acess Project
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
A minimal entrypoint to the Bitmask UI,
that depends on chromium being installed in the system.
"""

import commands
import os
import sys
import time

from multiprocessing import Process

from leap.bitmask.core.launcher import run_bitmaskd, pid
from leap.common.config import get_path_prefix


AUTHTOKEN_PATH = os.path.join(get_path_prefix(), 'leap', 'authtoken')


def get_url():
    url = "http://localhost:7070"
    waiting = 20
    while not os.path.isfile(AUTHTOKEN_PATH):
        if waiting == 0:
            # If we arrive here, something really messed up happened,
            # because touching the token file is one of the first
            # things the backend does, and this BrowserWindow
            # should be called *right after* launching the backend.
            raise NoAuthToken(
                'No authentication token found!')
        time.sleep(0.1)
        waiting -= 1
    token = open(AUTHTOKEN_PATH).read().strip()
    url += '#' + token
    return url


def delete_old_authtoken():
    try:
        os.remove(AUTHTOKEN_PATH)
    except OSError:
        pass


def start_app():
    if not commands.getoutput('which chromium'):
        print ('[!] Cannot find chromium installed in the system!')
        sys.exit(1)
    delete_old_authtoken()
    bitmaskd = Process(target=run_bitmaskd)
    bitmaskd.start()

    cmd = 'chromium -app=%s' % get_url()
    commands.getoutput(cmd)


class NoAuthToken(Exception):
    pass


if __name__ == "__main__":
    start_app()
