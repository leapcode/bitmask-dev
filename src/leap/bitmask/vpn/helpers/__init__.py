from os import remove, chmod, access, R_OK
from shutil import copyfile
from hashlib import sha512
import os.path
import sys

from leap.bitmask.vpn.constants import IS_LINUX, IS_MAC
from leap.bitmask.vpn import _config

from leap.bitmask.util import STANDALONE

if IS_LINUX:

    from leap.bitmask.vpn.constants import BITMASK_ROOT_SYSTEM
    from leap.bitmask.vpn.constants import BITMASK_ROOT_LOCAL
    from leap.bitmask.vpn.constants import OPENVPN_SYSTEM, OPENVPN_LOCAL
    from leap.bitmask.vpn.constants import POLKIT_SYSTEM, POLKIT_LOCAL
    from leap.bitmask.vpn.privilege import is_pkexec_in_system
    from leap.bitmask.vpn.privilege import LinuxPolicyChecker

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
            chmod(OPENVPN_LOCAL, 0744)

    def uninstall():
        remove(BITMASK_ROOT_LOCAL)
        remove(POLKIT_LOCAL)
        remove(OPENVPN_LOCAL)

    def privcheck(timeout=5):
        has_pkexec = is_pkexec_in_system()
        running = LinuxPolicyChecker.is_up()
        if not running:
            try:
                LinuxPolicyChecker.get_usable_pkexec(timeout=timeout)
                running = LinuxPolicyChecker.is_up()
            except Exception:
                running = False
        return has_pkexec and running

    def check():
        helper = _is_up_to_date(_config.get_bitmask_helper_path(),
                                BITMASK_ROOT_LOCAL,
                                BITMASK_ROOT_SYSTEM)
        polkit = _is_up_to_date(_config.get_bitmask_polkit_policy_path(),
                                POLKIT_LOCAL,
                                POLKIT_SYSTEM)
        openvpn = (os.path.exists(OPENVPN_SYSTEM) or
                   _is_up_to_date(_config.get_bitmask_openvpn_path(),
                                  OPENVPN_LOCAL, ""))
        return helper and polkit and openvpn

    def _is_up_to_date(src, local, system):
        if src is None or not access(src, R_OK):
            return True

        src_digest = digest(src)
        if access(system, R_OK) and src_digest == digest(system):
                return True
        if access(local, R_OK) and src_digest == digest(local):
                return True

        return False


elif IS_MAC:

    def check():
        # XXX check if bitmask-helper is running
        return True

    def privcheck():
        return True


def digest(path):
    with open(path, 'r') as f:
        s = f.read()
    return sha512(s).digest()


def main():
    if sys.argv[-1] == 'install':
        install()
    if sys.argv[-1] == 'uninstall':
        uninstall()


if __name__ == "__main__":
    main()
