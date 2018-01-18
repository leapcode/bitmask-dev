# -*- coding: utf-8 -*-
# polkit_agent.py
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
Daemonizes polkit authentication agent.
"""

import os
import subprocess


POLKIT_PATHS = (
    '/usr/bin/lxpolkit',
    '/usr/bin/lxqt-policykit-agent',
    '/usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1',
    '/usr/lib/x86_64-linux-gnu/polkit-mate/polkit-mate-authentication-agent-1',
    '/usr/lib/mate-polkit/polkit-mate-authentication-agent-1',
    '/usr/lib/x86_64-linux-gnu/libexec/polkit-kde-authentication-agent-1',
    '/usr/lib/kde4/libexec/polkit-kde-authentication-agent-1',
    # now we get weird
    '/usr/libexec/policykit-1-pantheon/pantheon-agent-polkit',
    '/usr/lib/polkit-1-dde/dde-polkit-agent',
    # do you know some we're still missing? :)
)

POLKIT_PROC_NAMES = (
    'polkit-gnome-authentication-agent-1',
    'polkit-kde-authentication-agent-1',
    'polkit-mate-authentication-agent-1',
    'lxpolkit',
    'lxsession',
    'gnome-shell',
    'gnome-flashback',
    'fingerprint-polkit-agent',
    'xfce-polkit',
)


# TODO write tests for this piece.
def _get_polkit_agent():
    """
    Return a valid polkit agent to use.

    :rtype: str or None
    """
    for polkit in POLKIT_PATHS:
        if os.path.isfile(polkit):
            return polkit
    return None


def launch():
    """
    Launch a polkit authentication agent as a daemon.
    """
    agent = _get_polkit_agent()
    subprocess.call("(setsid {polkit} &)".format(polkit=agent), shell=True)


if __name__ == "__main__":
    launch()
