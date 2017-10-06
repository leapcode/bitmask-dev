from os import remove, chmod
from shutil import copyfile
import os.path
import sys

from leap.bitmask.vpn.constants import IS_LINUX, IS_MAC
from leap.bitmask.vpn.constants import BITMASK_ROOT_SYSTEM, BITMASK_ROOT_LOCAL
from leap.bitmask.vpn.constants import OPENVPN_SYSTEM, OPENVPN_LOCAL
from leap.bitmask.vpn.constants import POLKIT_SYSTEM, POLKIT_LOCAL
from leap.bitmask.vpn.privilege import is_pkexec_in_system
from leap.bitmask.vpn import _config

from leap.bitmask.util import STANDALONE

if IS_LINUX:
    def install():
        helper_from = _config.get_bitmask_helper_path()
        polkit_from = _config.get_bitmask_polkit_policy_path()
        openvpn_from = _config.get_bitmask_openvpn_path()

        sbin = '/usr/local/sbin'
        if not os.path.isdir(sbin):
            os.makedirs(sbin)

        copyfile(helper_from, BITMASK_ROOT_LOCAL)
        chmod(BITMASK_ROOT_LOCAL, 0744)

        copyfile(polkit_from, POLKIT_LOCAL)

        if STANDALONE:
            copyfile(openvpn_from, OPENVPN_LOCAL)
            chmod(OPENVPN_LOCAL, 0700)

    def uninstall():
        remove(BITMASK_ROOT_LOCAL)
        remove(POLKIT_LOCAL)

    def check():
        helper = (
            os.path.exists(BITMASK_ROOT_LOCAL) or
            os.path.isfile(BITMASK_ROOT_SYSTEM))
        polkit = (
            os.path.exists(POLKIT_LOCAL) or
            os.path.exists(POLKIT_SYSTEM))
        openvpn = (
            os.path.exists(OPENVPN_LOCAL) or
            os.path.exists(OPENVPN_SYSTEM))

        return is_pkexec_in_system() and helper and polkit and openvpn

if IS_MAC:

    def check():
        # XXX check if bitmask-helper is running
        return True


def main():
    if sys.argv[-1] == 'install':
        install()
    if sys.argv[-1] == 'uninstall':
        uninstall()


if __name__ == "__main__":
    main()
