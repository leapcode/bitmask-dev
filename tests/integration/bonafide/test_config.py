# -*- coding: utf-8 -*-
# test_config.py
# Copyright (C) 2015-2017 LEAP
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
import os.path

from BaseHTTPServer import BaseHTTPRequestHandler
from twisted.internet import defer
from twisted.trial import unittest

from leap.bitmask.bonafide.config import Provider
from leap.bitmask.bonafide.errors import NetworkError
from leap.common.testing.basetest import BaseLeapTest
from leap.common.testing.https_server import BaseHTTPSServerTestCase


class ConfigTest(BaseHTTPSServerTestCase, unittest.TestCase, BaseLeapTest):

    def setUp(self):
        self.addr = Addr()
        self.request_handler = request_handler(self.addr)
        BaseHTTPSServerTestCase.setUp(self)
        self.addr.host = 'localhost'
        self.addr.port = self.PORT
        self.cacert = os.path.join(os.path.dirname(__file__),
                                   "cacert.pem")

    @defer.inlineCallbacks
    def test_bootstrap_self_sign_cert_fails(self):
        home = os.path.join(self.home, 'self_sign')
        os.mkdir(home)
        provider = Provider.get(self.addr.domain, autoconf=True, basedir=home)
        d = provider.callWhenMainConfigReady(lambda: "Cert was accepted")
        yield self.assertFailure(d, NetworkError)
        Provider.providers[self.addr.domain] = None

    @defer.inlineCallbacks
    def test_bootstrap_invalid_ca_cert(self):
        home = os.path.join(self.home, 'fp')
        os.mkdir(home)
        self.addr.fingerprint = "fabadafabada"
        provider = Provider(self.addr.domain, autoconf=True, basedir=home,
                            cert_path=self.cacert)

        d = provider.callWhenMainConfigReady(lambda: "CA cert fp matched")
        yield self.assertFailure(d, NetworkError)
        self.assertFalse(os.path.isfile(provider._get_ca_cert_path()))
        provider._http.close()
        try:
            yield defer.gatherResults([
                d, provider.ongoing_bootstrap])
        except:
            pass
        Provider.providers[self.addr.domain] = None

    @defer.inlineCallbacks
    def test_bootstrap_pinned_cert(self):
        home = os.path.join(self.home, 'pinned')
        os.mkdir(home)
        provider = Provider.get(self.addr.domain, autoconf=True, basedir=home,
                                cert_path=self.cacert)

        def check_provider():
            config = provider.config()
            self.assertEqual(config["domain"], self.addr.host)
            self.assertEqual(config["ca_cert_fingerprint"],
                             "SHA256: %s" % fingerprint)

        yield provider.callWhenMainConfigReady(check_provider)
        provider._http.close()
        yield provider.ongoing_bootstrap
        Provider.providers[self.addr.domain] = None

    @defer.inlineCallbacks
    def test_api_uri(self):
        api_uri = "api.example.com"
        self.addr.api_uri = api_uri
        home = os.path.join(self.home, 'api_uri')
        os.mkdir(home)
        provider = Provider.get(self.addr.domain, autoconf=True,
                                basedir=home, cert_path=self.cacert)

        def check_api_uri():
            parsed_uri = provider.api_uri
            self.assertEqual(api_uri, parsed_uri)

        yield provider.callWhenMainConfigReady(check_api_uri)
        provider._http.close()
        try:
            yield provider.ongoing_bootstrap
        except:
            pass
        Provider.providers[self.addr.domain] = None


class Addr(object):
    def __init__(self, host='localhost', port='4443'):
        self.host = host
        self.port = port
        self.fingerprint = fingerprint
        self.api_uri = "https://%s:%s" % (host, port)

    @property
    def domain(self):
        return "%s:%s" % (self.host, self.port)


def request_handler(addr):
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/provider.json':
                body = provider_json % {
                    'api_uri': addr.api_uri,
                    'host': addr.host,
                    'port': addr.port,
                    'fingerprint': addr.fingerprint
                }

            elif self.path == '/ca.crt':
                cacert = os.path.join(os.path.dirname(__file__),
                                      "leaptestscert.pem")
                with open(cacert, 'r') as f:
                    castr = f.read()
                body = castr

            elif self.path == '/1/configs.json':
                body = configs_json

            else:
                body = '{"error": "not implemented"}'

            self.send_response(200)
            self.send_header('Content-type', 'applicatino/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return RequestHandler


fingerprint = \
    "cd0131b3352b7a29c307156b24f09fe862b1f5a2e55be7cd888048b91770f220"
provider_json = """
{
  "api_uri": "%(api_uri)s",
  "api_version": "1",
  "ca_cert_fingerprint": "SHA256: %(fingerprint)s",
  "ca_cert_uri": "https://%(host)s:%(port)s/ca.crt",
  "default_language": "en",
  "description": {
    "en": "example"
  },
  "domain": "%(host)s",
  "enrollment_policy": "open",
  "languages": [
    "en"
  ],
  "name": {
    "en": "Bitmask"
  },
  "service": {
    "allow_anonymous": false,
    "allow_free": true,
    "allow_limited_bandwidth": false,
    "allow_paid": false,
    "allow_registration": true,
    "allow_unlimited_bandwidth": true,
    "bandwidth_limit": 102401,
    "default_service_level": 1,
    "levels": {
      "1": {
        "description": "hi.",
        "name": "free"
      }
    }
  },
  "services": []
}
"""
configs_json = "{}"
