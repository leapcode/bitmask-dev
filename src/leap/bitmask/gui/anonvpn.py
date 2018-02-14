# -*- coding: utf-8 -*-
# anonvpn.py
# Copyright (C) 2018 LEAP Encryption Acess Project
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
Entrypoint for an standalone systray binary.

Launches bitmaskd and then launches the systray.
"""

import subprocess
import os
import platform
import signal
import sys

from functools import partial
from multiprocessing import Process

from leap.bitmask.core.launcher import run_bitmaskd, pid
from leap.bitmask.gui.housekeeping import cleanup, terminate, reset_authtoken
from leap.bitmask.gui.housekeeping import check_stale_pidfile
from leap.bitmask.gui.housekeeping import NoAuthTokenError
from leap.common.config import get_path_prefix


bitmaskd = None


def launch_gui():
    from leap.bitmask.util import STANDALONE
    if STANDALONE:
        gui = './bitmask-systray'
    else:
        gui = 'bitmask-systray'
    subprocess.call([gui])


def start_app():
    global bitmaskd

    check_stale_pidfile()
    bitmaskd = Process(target=run_bitmaskd)
    bitmaskd.start()
    reset_authtoken()
    launch_gui()
    print "[anonvpn] Systray Quitted."
    bitmaskd.join()
    terminate(pid)
    cleanup()


if __name__ == "__main__":
    start_app()
