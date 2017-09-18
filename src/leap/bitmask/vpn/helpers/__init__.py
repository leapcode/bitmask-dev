from os import remove, chmod
from shutil import copyfile
import os.path
import sys

from leap.bitmask.vpn.constants import IS_LINUX, IS_MAC
from leap.bitmask.vpn.privilege import is_pkexec_in_system
from leap.bitmask.vpn import _config

from leap.bitmask.util import STANDALONE

if IS_LINUX:

    helper_to = '/usr/local/sbin/bitmask-root'
    polkit_to = '/usr/share/polkit-1/actions/se.leap.bitmask-bundle.policy'
    deb_polkit_to = '/usr/share/polkit-1/actions/se.leap.bitmask.policy'
    openvpn_to = '/usr/local/sbin/leap-openvpn'

    def install():
        helper_from = _config.get_bitmask_helper_path()
        polkit_from = _config.get_bitmask_polkit_policy_path()
        openvpn_from = _config.get_bitmask_openvpn_path()

        copyfile(helper_from, helper_to)
        chmod(helper_to, 0744)

        copyfile(polkit_from, polkit_to)

        if STANDALONE:
            copyfile(openvpn_from, openvpn_to)
            chmod(openvpn_to, 0700)

    def uninstall():
        remove(helper_to)
        remove(polkit_to)

    def check():
        helper = os.path.exists(helper_to)
        polkit = (
            os.path.exists(polkit_to) or
            os.path.exists(deb_polkit_to))
        return is_pkexec_in_system() and helper and polkit

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
