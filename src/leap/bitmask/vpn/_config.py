import pkg_resources
from .constants import IS_LINUX


if IS_LINUX:

    def get_bitmask_helper_path():
        return pkg_resources.resource_filename(
            'leap.bitmask.vpn.helpers.linux', 'bitmask-root')

    def get_bitmask_polkit_policy_path():
        return pkg_resources.resource_filename(
            'leap.bitmask.vpn.helpers.linux', 'se.leap.bitmask.bundle.policy')


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

