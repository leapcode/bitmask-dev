# -*- coding: utf-8 -*-
# autostart.py
# Copyright (C) 2018 LEAP
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
Autostart bitmask on user login
"""
import os
import os.path

from leap.bitmask.system import IS_LINUX, IS_MAC
from leap.common.config import get_path_prefix
from leap.bitmask.core import flags

if IS_LINUX:
    AUTOSTART = r"""[Desktop Entry]
Name=%(name)s
Type=Application
Exec=%(exec)s
Path=%(path)s
Terminal=false
"""

    def autostart_app(status):
        """
        Leave an autostart file in the user's autostart path.

        The bundle could in principle find its own path and add
        the path to the bitmaskd binary in the Exec entry.
        But for now it's simpler to do autostart only for the debian packages
        or any other method that puts bitmask in the path.
        On the other hand, we want to reduce the modifications that the bundle
        leaves behind.
        """
        if not flags.APP_NAME or not flags.EXEC_PATH:
            return

        config = get_path_prefix(standalone=False)
        autostart_file = os.path.join(config, 'autostart',
                                      '%s.desktop' % flags.APP_NAME)
        if status == 'on':
            _dir = os.path.split(autostart_file)[0]
            if not os.path.isdir(_dir):
                os.makedirs(_dir)
            with open(autostart_file, 'w') as f:
                f.write(AUTOSTART % {
                        'name': flags.APP_NAME,
                        'exec': flags.EXEC_PATH,
                        'path': os.getcwd()
                        })
        elif status == 'off':
            try:
                os.unlink(autostart_file)
            except OSError:
                pass

if IS_MAC:

    def autostart_app(status):
        pass
