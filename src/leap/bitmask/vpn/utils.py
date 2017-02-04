# -*- coding: utf-8 -*-
# util.py
# Copyright (C) 2013-2017 LEAP
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
Common utils
"""


def force_eval(items):
    """
    Return a sequence that evaluates any callable in the sequence,
    instantiating it beforehand if the item is a class, and
    leaves the non-callable items without change.
    """
    def do_eval(thing):
        if isinstance(thing, type):
            return thing()()
        if callable(thing):
            return thing()
        return thing

    if isinstance(items, (list, tuple)):
        return map(do_eval, items)
    else:
        return do_eval(items)


def first(things):
    """
    Return the head of a collection.

    :param things: a sequence to extract the head from.
    :type things: sequence
    :return: object, or None
    """
    try:
        return things[0]
    except (IndexError, TypeError):
        return None


def get_vpn_launcher():
    """
    Return the VPN launcher for the current platform.
    """
    from leap.bitmask.vpn.constants import IS_LINUX, IS_MAC, IS_WIN

    if not (IS_LINUX or IS_MAC or IS_WIN):
        error_msg = "VPN Launcher not implemented for this platform."
        raise NotImplementedError(error_msg)

    launcher = None
    if IS_LINUX:
        from leap.bitmask.vpn.launchers.linux import LinuxVPNLauncher
        launcher = LinuxVPNLauncher
    elif IS_MAC:
        from leap.bitmask.vpn.launchers.darwin import DarwinVPNLauncher
        launcher = DarwinVPNLauncher
    elif IS_WIN:
        from leap.bitmask.vpn.launchers.windows import WindowsVPNLauncher
        launcher = WindowsVPNLauncher

    if launcher is None:
        raise Exception("Launcher is None")

    return launcher()
