# -*- coding: utf-8 -*-
# manager.py
# Copyright (C) 2015 LEAP
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
VPN Manager
"""

import os
import tempfile

from ._control import VPNControl
from ._config import _TempVPNConfig, _TempProviderConfig
from .constants import IS_WIN


# TODO this is very badly named. There is another class that is called
# manager. This

class TunnelManager(object):

    def __init__(self, provider, remotes, cert_path, key_path, ca_path,
                 extra_flags):
        """
        Initialize the VPNManager object.

        :param remotes: a list of gateways tuple (ip, port) looking like this:
            ((ip1, portA), (ip2, portB), ...)
        :type remotes: tuple of tuple(str, int)
        """
        # TODO we can set all the needed ports, gateways and paths in here
        # TODO need gateways here
        # sorting them doesn't belong in here
        # gateways = ((ip1, portA), (ip2, portB), ...)

        ports = []

        self._remotes = remotes

        self._vpnconfig = _TempVPNConfig(extra_flags, cert_path, ports)
        self._providerconfig = _TempProviderConfig(provider, ca_path)

        host, port = self._get_management_location()
        self._vpn = VPNControl(remotes=remotes,
                               vpnconfig=self._vpnconfig,
                               providerconfig=self._providerconfig,
                               socket_host=host, socket_port=port)

    def start(self):
        """
        Start the VPN process.
        """
        result = self._vpn.start()
        return result

    def stop(self):
        """
        Bring openvpn down using the privileged wrapper.

        :returns: True if succeeded, False otherwise.
        :rtype: bool
        """
        # TODO how to return False if this fails
        result = self._vpn.stop(False, False)  # TODO review params
        return result

    @property
    def status(self):
        return self._vpn.status

    @property
    def traffic_status(self):
        return self._vpn.traffic_status

    def _get_management_location(self):
        """
        Return a tuple with the host (socket) and port to be used for VPN.

        :return: (host, port)
        :rtype: tuple (str, str)
        """
        if IS_WIN:
            host = "localhost"
            port = "9876"
        else:
            # XXX cleanup this on exit too
            # XXX atexit.register ?
            host = os.path.join(tempfile.mkdtemp(prefix="leap-tmp"),
                                'openvpn.socket')
            port = "unix"

        return host, port
