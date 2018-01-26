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
        return (
            is_pkexec_in_system() and
            _check_helper() and
            _check_polkit_file_exist() and
            _check_openvpn())

    def _check_helper():
        helper_path = _config.get_bitmask_helper_path()
        if not _exists_and_can_read(helper_path):
            return True

        helper_path_digest = digest(helper_path)
        if (_exists_and_can_read(BITMASK_ROOT_SYSTEM) and
                helper_path_digest == digest(BITMASK_ROOT_SYSTEM)):
                return True
        if (_exists_and_can_read(BITMASK_ROOT_LOCAL) and
                helper_path_digest == digest(BITMASK_ROOT_LOCAL)):
                return True

        return False

    def _check_openvpn():
        if os.path.exists(OPENVPN_SYSTEM):
            return True

        openvpn_path = _config.get_bitmask_openvpn_path()
        if openvpn_path is None:
            # If there bitmask doesn't provide any openvpn binary (we are not
            # in a bundle), reporting an error on check will trigger an attempt
            # to install helpers that can not succeed.
            # XXX: we need a better way to flag errors that can not be solved
            # by installing helpers
            return True

        openvpn_path_digest = digest(openvpn_path)
        if (_exists_and_can_read(OPENVPN_LOCAL) and
                openvpn_path_digest == digest(OPENVPN_LOCAL)):
                return True

        return False

    def _check_polkit_file_exist():
        # XXX: we are just checking if there is any policy file installed not
        # if it's valid or if it's the correct one that will be used.
        # (if LOCAL is used if /usr/local/sbin/bitmask-root is used and SYSTEM
        # if /usr/sbin/bitmask-root)
        return (os.path.exists(POLKIT_LOCAL) or
                os.path.exists(POLKIT_SYSTEM))

    def _exists_and_can_read(file_path):
        return access(file_path, R_OK)


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
