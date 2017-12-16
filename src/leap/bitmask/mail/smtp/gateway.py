# -*- coding: utf-8 -*-
# gateway.py
# Copyright (C) 2013 LEAP
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
"""
LEAP SMTP encrypted gateway.

The following classes comprise the SMTP gateway service:

    * SMTPFactory - A twisted.internet.protocol.ServerFactory that provides
      the SMTPDelivery protocol.

    * SMTPDelivery - A twisted.mail.smtp.IMessageDelivery implementation. It
      knows how to validate sender and receiver of messages and it generates
      an EncryptedMessage for each recipient.

    * EncryptedMessage - An implementation of twisted.mail.smtp.IMessage that
      knows how to encrypt/sign itself before sending.
"""
from email import generator
from email.Header import Header

from zope.interface import implements
from zope.interface import implementer

from twisted.cred.portal import Portal, IRealm
from twisted.mail import smtp
from twisted.mail.imap4 import LOGINCredentials, PLAINCredentials
from twisted.internet import protocol
from twisted.logger import Logger

from leap.common.check import leap_assert_type
from leap.common.events import emit_async, catalog
from leap.bitmask.mail import errors
from leap.bitmask.mail.cred import LocalSoledadTokenChecker
from leap.bitmask.mail.utils import validate_address
from leap.bitmask.mail.rfc3156 import RFC3156CompliantGenerator

# replace email generator with a RFC 3156 compliant one.
generator.Generator = RFC3156CompliantGenerator

LOCAL_FQDN = "bitmask.local"


@implementer(IRealm)
class LocalSMTPRealm(object):

    _encoding = 'utf-8'

    def __init__(self, outgoing_sessions, encrypted_only=False):
        self._outgoing_sessions = outgoing_sessions
        self.encrypted_only = encrypted_only

    def requestAvatar(self, avatarId, mind, *interfaces):
        if smtp.IMessageDelivery not in interfaces:
            raise NotImplementedError(self, interfaces)

        if isinstance(avatarId, str):
            avatarId = avatarId.decode(self._encoding)

        outgoing = self.lookupOutgoingInstance(avatarId)
        avatar = SMTPDelivery(avatarId, self.encrypted_only, outgoing)
        return (smtp.IMessageDelivery, avatar,
                getattr(avatar, 'logout', lambda: None))

    def lookupOutgoingInstance(self, userid):
        try:
            outgoing = self._outgoing_sessions[userid]
        except:
            raise errors.AuthenticationError(
                'No outgoing session found for user %s. Is it authenticated?'
                % userid)
        return outgoing


class SMTPTokenChecker(LocalSoledadTokenChecker):
    """A credentials checker that will lookup a token for the SMTP service.
    For now it will be using the same identifier than IMAPTokenChecker"""

    service = 'mail_auth'

    # TODO besides checking for token credential,
    # we could also verify the certificate here.


class LEAPInitMixin(object):

    """
    A Mixin that takes care of initialization of all the data needed to access
    LEAP sessions.
    """
    def __init__(self, outgoing_sessions, soledad_sessions,
                 encrypted_only=False):
        realm = LocalSMTPRealm(outgoing_sessions, encrypted_only)
        portal = Portal(realm)

        checker = SMTPTokenChecker(soledad_sessions)
        self.checker = checker
        self.portal = portal
        portal.registerChecker(checker)


class LocalSMTPServer(smtp.ESMTP, LEAPInitMixin):
    """
    The Production ESMTP Server: Authentication Needed.
    Authenticates against SMTP Token stored in Local Soledad instance.
    The Realm will produce a Delivery Object that handles encryption/signing.
    """

    # TODO: implement Queue using twisted.mail.mail.MailService

    def __init__(self, outgoings, soledads, encrypted_only=False):
        LEAPInitMixin.__init__(self, outgoings, soledads, encrypted_only)
        smtp.ESMTP.__init__(self)


# TODO implement retries -- see smtp.SenderMixin
class SMTPFactory(protocol.ServerFactory):
    """
    Factory for an SMTP server with encrypted gatewaying capabilities.
    """

    protocol = LocalSMTPServer
    domain = LOCAL_FQDN
    timeout = 600
    encrypted_only = False

    def __init__(self, outgoing_sessions, soledad_sessions, deferred=None,
                 retries=3):
        self._outgoing_sessions = outgoing_sessions
        self._soledad_sessions = soledad_sessions

    def buildProtocol(self, addr):
        p = self.protocol(self._outgoing_sessions, self._soledad_sessions,
                          encrypted_only=self.encrypted_only)
        p.factory = self
        p.host = LOCAL_FQDN
        p.challengers = {"LOGIN": LOGINCredentials, "PLAIN": PLAINCredentials}
        return p


#
# SMTPDelivery
#

@implementer(smtp.IMessageDelivery)
class SMTPDelivery(object):

    """
    Validate email addresses and handle message delivery.
    """

    log = Logger()

    def __init__(self, userid, encrypted_only, outgoing_mail):
        """
        Initialize the SMTP delivery object.

        :param userid: The user currently logged in
        :type userid: unicode
        :param encrypted_only: Whether the SMTP gateway should send unencrypted
                               mail or not.
        :type encrypted_only: bool
        :param outgoing_mail: The outgoing mail to send the message
        :type outgoing_mail: leap.bitmask.mail.outgoing.service.OutgoingMail
        """
        self._userid = userid
        self._outgoing = outgoing_mail
        self._encrypted_only = encrypted_only
        self._origin = None

    def receivedHeader(self, helo, origin, recipients):
        """
        Generate the 'Received:' header for a message.

        :param helo: The argument to the HELO command and the client's IP
            address.
        :type helo: (str, str)
        :param origin: The address the message is from.
        :type origin: twisted.mail.smtp.Address
        :param recipients: A list of the addresses for which this message is
            bound.
        :type: list of twisted.mail.smtp.User

        @return: The full "Received" header string.
        :type: str
        """
        myHostname, clientIP = helo
        headerValue = "by bitmask.local from %s with ESMTP ; %s" % (
            clientIP, smtp.rfc822date())
        # email.Header.Header used for automatic wrapping of long lines
        return "Received: %s" % Header(s=headerValue, header_name='Received')

    def validateTo(self, user):
        """
        Validate the address of a recipient of the message, possibly
        rejecting it if the recipient key is not available.

        This method is called once for each recipient, i.e. for each SMTP
        protocol line beginning with "RCPT TO:", which includes all addresses
        in "To", "Cc" and "Bcc" MUA fields.

        The recipient's address is validated against the RFC 2822 definition.
        If self._encrypted_only is True and no key is found for a recipient,
        then that recipient is rejected.

        The method returns an encrypted message object that is able to send
        itself to the user's address.

        :param user: The user whose address we wish to validate.
        :type: twisted.mail.smtp.User

        @return: A callable which takes no arguments and returns an
                 encryptedMessage.
        @rtype: no-argument callable

        @raise SMTPBadRcpt: Raised if messages to the address are not to be
                            accepted.
        """
        # try to find recipient's public key
        address = validate_address(user.dest.addrstr)

        def verify_if_can_encrypt_for_recipient(can_encrypt):
            if can_encrypt:
                self.log.debug('Accepting mail for %s...' % user.dest.addrstr)
                emit_async(catalog.SMTP_RECIPIENT_ACCEPTED_ENCRYPTED,
                           self._userid, user.dest.addrstr)
            elif self._encrypted_only:
                emit_async(catalog.SMTP_RECIPIENT_REJECTED, self._userid,
                           user.dest.addrstr)
                raise smtp.SMTPBadRcpt(user.dest.addrstr)
            else:
                self.log.warn(
                    'Warning: will send an unencrypted message (because '
                    '"encrypted_only" is set to False).')
                emit_async(
                    catalog.SMTP_RECIPIENT_ACCEPTED_UNENCRYPTED,
                    self._userid, user.dest.addrstr)

        def encrypt_func(_):
            return lambda: EncryptedMessage(user, self._outgoing)

        d = self._outgoing.can_encrypt_for(address)
        d.addCallback(verify_if_can_encrypt_for_recipient)
        d.addCallback(encrypt_func)
        return d

    def validateFrom(self, helo, origin):
        """
        Validate the address from which the message originates.

        :param helo: The argument to the HELO command and the client's IP
            address.
        :type: (str, str)
        :param origin: The address the message is from.
        :type origin: twisted.mail.smtp.Address

        @return: origin or a Deferred whose callback will be passed origin.
        @rtype: Deferred or Address

        @raise twisted.mail.smtp.SMTPBadSender: Raised if messages from this
            address are not to be accepted.
        """
        # accept mail from anywhere. To reject an address, raise
        # smtp.SMTPBadSender here.
        if str(origin) != str(self._userid):
            self.log.error(
                "Rejecting sender {0}, expected {1}".format(origin,
                                                            self._userid))
            raise smtp.SMTPBadSender(origin)
        self._origin = origin
        return origin


#
# EncryptedMessage
#

class EncryptedMessage(object):
    """
    Receive plaintext from client, encrypt it and send message to a
    recipient.
    """
    implements(smtp.IMessage)
    log = Logger()

    def __init__(self, user, outgoing_mail):
        """
        Initialize the encrypted message.

        :param user: The recipient of this message.
        :type user: twisted.mail.smtp.User
        :param outgoing_mail: The outgoing mail to send the message
        :type outgoing_mail: leap.bitmask.mail.outgoing.service.OutgoingMail
        """
        # assert params
        leap_assert_type(user, smtp.User)

        self._user = user
        self._lines = []
        self._outgoing = outgoing_mail

    def lineReceived(self, line):
        """
        Handle another line.

        :param line: The received line.
        :type line: str
        """
        self._lines.append(line)

    def eomReceived(self):
        """
        Handle end of message.

        This method will encrypt and send the message.

        :returns: a deferred
        """
        self.log.debug('Message data complete.')
        self._lines.append('')  # add a trailing newline
        raw_mail = '\r\n'.join(self._lines)

        return self._outgoing.send_message(raw_mail, self._user)

    def connectionLost(self):
        """
        Log an error when the connection is lost.
        """
        self.log.error('Connection lost unexpectedly!')
        emit_async(catalog.SMTP_CONNECTION_LOST, self._userid,
                   self._user.dest.addrstr)
        # unexpected loss of connection; don't save

        self._lines = []
