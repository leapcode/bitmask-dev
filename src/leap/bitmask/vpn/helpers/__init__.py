from os import remove
from shutil import copyfile
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
        copyfile(polkit_from, polkit_to)

    def uninstall():
        try:
            remove(helper_to)
            remove(polkit_to)
        except:
            raise


def main():
    if sys.argv[-1] == 'install':
        install()
    if sys.argv[-1] == 'uninstall':
        uninstall()


if __name__ == "__main__":
    main()
