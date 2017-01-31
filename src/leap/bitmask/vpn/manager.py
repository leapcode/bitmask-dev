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

from leap.bitmask.vpn import process
from leap.bitmask.vpn.constants import IS_WIN


class _TempEIPConfig(object):
    """Current EIP code on bitmask depends on EIPConfig object, this temporary
    implementation helps on the transition."""

    def __init__(self, flags, path, ports):
        self._flags = flags
        self._path = path
        self._ports = ports

    def get_gateway_ports(self, idx):
        return self._ports

    def get_openvpn_configuration(self):
        return self._flags

    def get_client_cert_path(self, providerconfig):
        return self._path


class _TempProviderConfig(object):
    """Current EIP code on bitmask depends on ProviderConfig object, this
    temporary implementation helps on the transition."""

    def __init__(self, domain, path):
        self._domain = domain
        self._path = path

    def get_domain(self):
        return self._domain

    def get_ca_cert_path(self):
        return self._path


class VPNManager(object):

    def __init__(self, remotes, cert_path, key_path, ca_path, extra_flags,
                 mock_signaler):
        """
        Initialize the VPNManager object.

        :param remotes: a list of gateways tuple (ip, port) looking like this:
            ((ip1, portA), (ip2, portB), ...)
        :type remotes: tuple of tuple(str, int)
        """
        # TODO we can set all the needed ports, gateways and paths in here
        ports = []

        # this seems to be obsolete, needed to get gateways
        domain = "demo.bitmask.net"
        self._remotes = remotes

        self._eipconfig = _TempEIPConfig(extra_flags, cert_path, ports)
        self._providerconfig = _TempProviderConfig(domain, ca_path)
        # signaler = None  # XXX handle signaling somehow...
        signaler = mock_signaler
        self._vpn = process.VPN(remotes=remotes, signaler=signaler)

    def start(self):
        """
        Start the VPN process.

        VPN needs:
        * paths for: cert, key, ca
        * gateway, port
        * domain name
        """
        host, port = self._get_management()

        # TODO need gateways here
        # sorting them doesn't belong in here
        # gateways = ((ip1, portA), (ip2, portB), ...)

        self._vpn.start(eipconfig=self._eipconfig,
                        providerconfig=self._providerconfig,
                        socket_host=host, socket_port=port)
        return True

    def stop(self):
        """
        Bring openvpn down using the privileged wrapper.

        :returns: True if succeeded, False otherwise.
        :rtype: bool
        """
        self._vpn.terminate(False, False)  # TODO review params

        # TODO how to return False if this fails
        return True

    def is_up(self):
        """
        Return whether the VPN is up or not.

        :rtype: bool
        """
        pass

    def kill(self):
        """
        Sends a kill signal to the openvpn process.
        """
        pass
        # self._vpn.killit()

    def terminate(self):
        """
        Stop the openvpn subprocess.

        Attempts to send a SIGTERM first, and after a timeout it sends a
        SIGKILL.
        """
        pass

    def _get_management(self):
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
