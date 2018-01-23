import os
import os.path

from leap.bitmask.vpn.constants import IS_LINUX, IS_MAC
from leap.bitmask.util import STANDALONE
from leap.common.config import get_path_prefix

if IS_LINUX:
    AUTOSTART = r"""[Desktop Entry]
Name=Bitmask
Type=Application
Exec=bitmask
Terminal=false
"""
    config = get_path_prefix(standalone=False)
    autostart_file = os.path.join(config, 'autostart', 'bitmask.desktop')

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
        if not STANDALONE:
            if status == 'on':
                _dir = os.path.split(autostart_file)[0]
                if not os.path.isdir(_dir):
                    os.makedirs(_dir)
                with open(autostart_file, 'w') as f:
                    f.write(AUTOSTART)
            elif status == 'off':
                try:
                    os.unlink(autostart_file)
                except OSError:
                    pass

if IS_MAC:

    def autostart_app(status):
        pass
