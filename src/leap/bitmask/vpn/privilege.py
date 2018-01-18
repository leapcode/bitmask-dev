# -*- coding: utf-8 -*-
# privilege_policies.py
# Copyright (C) 2013 LEAP
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
Helpers to determine if the needed policies for privilege escalation
are operative under this client run.
"""

import commands
import os
import psutil
import time

from twisted.logger import Logger
from twisted.python.procutils import which

from leap.bitmask.util import STANDALONE, here
from .constants import IS_LINUX
from . import polkit

log = Logger()


# TODO wrap the install/uninstall helper functions around the policychecker
# classes below.


def install_helpers():
    _helper_installer('install')


def uninstall_helpers():
    _helper_installer('uninstall')


def _helper_installer(action):
    if action not in ('install', 'uninstall'):
        raise Exception('Wrong action: %s' % action)

    if IS_LINUX:
        cmd = 'bitmask_helpers ' + action
        if STANDALONE:
            binary_path = os.path.join(here(), "bitmask")
            cmd = "%s %s" % (binary_path, cmd)
        if os.getuid() != 0:
            cmd = 'pkexec ' + cmd
        retcode, output = commands.getstatusoutput(cmd)
        if retcode != 0:
            log.error('Error installing/uninstalling helpers: %s' % output)
            log.error('Command was: %s' % cmd)
            raise Exception('Could not install/uninstall helpers')
    else:
        raise Exception('No install mechanism for this platform')


class NoPolkitAuthAgentAvailable(Exception):
    message = 'No polkit authentication agent available. Please run one.'


class NoPkexecAvailable(Exception):
    message = 'Could not find pkexec in the system'


class LinuxPolicyChecker(object):
    """
    PolicyChecker for Linux
    """
    LINUX_POLKIT_FILE = ("/usr/share/polkit-1/actions/"
                         "se.leap.bitmask.policy")
    LINUX_POLKIT_FILE_BUNDLE = ("/usr/share/polkit-1/actions/"
                                "se.leap.bitmask.bundle.policy")
    PKEXEC_BIN = 'pkexec'

    @classmethod
    def get_polkit_path(self):
        """
        Returns the polkit file path.

        :rtype: str
        """
        return (self.LINUX_POLKIT_FILE_BUNDLE if STANDALONE
                else self.LINUX_POLKIT_FILE)

    @classmethod
    def get_usable_pkexec(self, timeout=20):
        """
        Checks whether pkexec is available in the system, and
        returns the path if found.

        Might raise:
            NoPkexecAvailable,
            NoPolkitAuthAgentAvailable.

        :returns: a list of the paths where pkexec is to be found
        :rtype: list
        """
        if not is_pkexec_in_system():
            log.warn('System has no pkexec')
            raise NoPkexecAvailable()

        if not self.is_up():
            self.launch()
            seconds = 0
            while not self.is_up():
                if seconds >= timeout:
                    log.warn('No polkit auth agent found. pkexec ' +
                             'will use its own auth agent.')
                    raise NoPolkitAuthAgentAvailable()
                time.sleep(1)
                seconds += 1

        pkexec_choices = which(self.PKEXEC_BIN)
        if not pkexec_choices:
            raise Exception("We couldn't find pkexec")
        return pkexec_choices

    @classmethod
    def launch(self):
        """
        Tries to launch polkit agent.
        """
        if not self.is_up():
            polkit.launch()

    @classmethod
    def is_up(self):
        """
        Checks if a polkit daemon is running.

        :return: True if it's running, False if it's not.
        :rtype: boolean
        """
        # Note that gnome-shell does not uses a separate process for the
        # polkit-agent, it uses a polkit-agent within its own process so we
        # can't ps-grep a polkit process, we can ps-grep gnome-shell itself.

        running = False
        for proc in psutil.process_iter():
            if any((pk in proc.name() for pk in polkit.POLKIT_PROC_NAMES)):
                running = True
                break
        return running


def is_pkexec_in_system():
    """
    Checks the existence of the pkexec binary in system.
    """
    pkexec_path = which('pkexec')
    if len(pkexec_path) == 0:
        return False
    return True
