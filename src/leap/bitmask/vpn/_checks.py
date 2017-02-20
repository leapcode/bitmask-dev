import os

from leap.common.config import get_path_prefix


# TODO use privilege.py module, plenty of checks in there for pkexec and
# friends.

class ImproperlyConfigured(Exception):
    pass


def is_service_ready(provider):
    _has_valid_cert(provider)
    return True


def get_vpn_cert_path(provider):
    return os.path.join(get_path_prefix(),
                        'leap', 'providers', provider,
                        'keys', 'client', 'openvpn.pem')


def _has_valid_cert(provider):
    cert_path = get_vpn_cert_path(provider)
    has_file = os.path.isfile(cert_path)
    if not has_file:
        raise ImproperlyConfigured('Missing VPN certificate')
