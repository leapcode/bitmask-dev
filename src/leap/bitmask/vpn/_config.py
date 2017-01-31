
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

