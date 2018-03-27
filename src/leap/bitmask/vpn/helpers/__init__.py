import os.path
import sys

from os import remove, chmod, access, R_OK
from shutil import copyfile
from hashlib import sha512

from twisted.logger import Logger

from leap.bitmask.vpn import _config

from leap.bitmask.system import IS_LINUX, IS_MAC, IS_SNAP
from leap.bitmask.util import STANDALONE

log = Logger()

if IS_LINUX:

    from leap.bitmask.vpn.constants import BITMASK_ROOT_SYSTEM
    from leap.bitmask.vpn.constants import BITMASK_ROOT_LOCAL
    from leap.bitmask.vpn.constants import OPENVPN_SYSTEM, OPENVPN_LOCAL
    from leap.bitmask.vpn.constants import OPENVPN_SNAP
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
        result = has_pkexec and running
        log.debug('Privilege check: %s' % result)
        return result

    def check():
        pkexec = is_pkexec_in_system()
        helper = _check_helper()
        polkit = _check_polkit_file_exist()
        openvpn = _check_openvpn()
        if not pkexec:
            log.error('No pkexec in system!')
        if not helper:
            log.error('No bitmask-root in system!')
        if not polkit:
            log.error('No polkit file in system!')
        if not openvpn:
            log.error('No openvpn in system!')
        result = all([pkexec, helper, polkit, openvpn])
        if result is True:
            log.debug('All checks passed')
        return result

    def _check_helper():
        log.debug('Checking whether helper exists')
        helper_path = _config.get_bitmask_helper_path()
        if not _exists_and_can_read(helper_path):
            log.debug('Cannot read helpers')
            return True

        if IS_SNAP:
            if os.path.isfile(BITMASK_ROOT_LOCAL):
                return True
            log.error('Cannot find bitmask-root in snap')
            return False

        helper_path_digest = digest(helper_path)
        if (_exists_and_can_read(BITMASK_ROOT_SYSTEM) and
                helper_path_digest == digest(BITMASK_ROOT_SYSTEM)):
            log.debug('Global bitmask-root: %s'
                      % os.path.isfile(BITMASK_ROOT_SYSTEM))
            return True
        if (_exists_and_can_read(BITMASK_ROOT_LOCAL) and
                helper_path_digest == digest(BITMASK_ROOT_LOCAL)):
            log.debug('Local bitmask-root: %s'
                      % os.path.isfile(BITMASK_ROOT_LOCAL))
            return True

        log.debug('No valid bitmask-root found')
        return False

    def _check_openvpn():
        if IS_SNAP:
            return os.path.exists(OPENVPN_SNAP)

        if os.path.exists(OPENVPN_SYSTEM):
            return True

        openvpn_path = _config.get_bitmask_openvpn_path()
        if openvpn_path is None:
            # If Bitmask does not provide any openvpn binary
            # (we are not in a bundle: either running from debian packages, git
            # or pip) reporting an error on check will trigger an attempt to
            # install helpers that can not be successful.
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

    def privcheck(timeout=5):
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
