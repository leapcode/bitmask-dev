from os import remove, chmod
from shutil import copyfile
import os.path
import sys

from leap.bitmask.vpn.constants import IS_LINUX
from leap.bitmask.vpn import _config

if IS_LINUX:

    helper_to = '/usr/local/sbin/bitmask-root'
    polkit_to = '/usr/share/polkit-1/actions/se.bitmask.bundle.policy'

    def install():
        helper_from = _config.get_bitmask_helper_path()
        polkit_from = _config.get_bitmask_polkit_policy_path()
        copyfile(helper_from, helper_to)
        chmod(helper_to, 0744)
        copyfile(polkit_from, polkit_to)

    def uninstall():
        remove(helper_to)
        remove(polkit_to)

    def check():
        helper = os.path.exists(helper_to)
        polkit = os.path.exists(polkit_to)
        return helper and polkit


def main():
    if sys.argv[-1] == 'install':
        install()
    if sys.argv[-1] == 'uninstall':
        uninstall()


if __name__ == "__main__":
    main()
