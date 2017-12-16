# -*- coding: utf-8 -*-
# outgoing/sender.py
# Copyright (C) 2017 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from OpenSSL import SSL
from StringIO import StringIO
from twisted.internet import reactor
from twisted.internet import defer
from twisted.logger import Logger
from twisted.mail import smtp
from twisted.protocols.amp import ssl
from zope.interface import Interface, implements

from leap.common.check import leap_assert_type, leap_assert
from leap.bitmask import __version__


class ISender(Interface):
    def can_send(self, recipient):
        """
        Checks if ISender implementor can send messages to recipient

        :type recipient: string
        :rtype: bool
        """

    def send(self, recipient, message):
        """
        Send a messages to recipient

        :type recipient: string
        :type message: string

        :return: A Deferred that will be called with the recipient address
        :raises SendError: in case of failure in send
        """


class SendError(Exception):
    pass


class SMTPSender(object):
    implements(ISender)

    log = Logger()

    def __init__(self, from_address, key, host, port):
        """
        :param from_address: The sender address.
        :type from_address: str
        :param key: The client private key for SSL authentication.
        :type key: str
        :param host: The hostname of the remote SMTP server.
        :type host: str
        :param port: The port of the remote SMTP server.
        :type port: int
        """
        leap_assert_type(host, (str, unicode))
        leap_assert(host != '')
        leap_assert_type(port, int)
        leap_assert(port is not 0)
        leap_assert_type(key, basestring)
        leap_assert(key != '')

        self._port = port
        self._host = host
        self._key = key
        self._from_address = from_address

    def can_send(self, recipient):
        return '@' in recipient

    def send(self, recipient, message):
        self.log.info(
            'Connecting to SMTP server %s:%s' % (self._host, self._port))

        # we construct a defer to pass to the ESMTPSenderFactory
        d = defer.Deferred()
        # we don't pass an ssl context factory to the ESMTPSenderFactory
        # because ssl will be handled by reactor.connectSSL() below.
        factory = smtp.ESMTPSenderFactory(
            "",  # username is blank, no client auth here
            "",  # password is blank, no client auth here
            self._from_address,
            recipient.dest.addrstr,
            StringIO(message),
            d,
            heloFallback=True,
            requireAuthentication=False,
            requireTransportSecurity=True)
        factory.domain = bytes('leap.bitmask.mail-' + __version__)
        reactor.connectSSL(
            self._host, self._port, factory,
            contextFactory=SSLContextFactory(self._key, self._key))
        d.addCallback(lambda result: result[1][0][0])
        d.addErrback(self._send_errback)
        return d

    def _send_errback(self, failure):
        raise SendError(failure.getErrorMessage())


class SSLContextFactory(ssl.ClientContextFactory):
    def __init__(self, cert, key):
        self.cert = cert
        self.key = key

    def getContext(self):
        # FIXME -- we should use sslv23 to allow for tlsv1.2
        # and, if possible, explicitely disable sslv3 clientside.
        # Servers should avoid sslv3
        self.method = SSL.TLSv1_METHOD  # SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file(self.cert)
        ctx.use_privatekey_file(self.key)
        return ctx
