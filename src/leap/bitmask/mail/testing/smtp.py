from twisted.mail import smtp

from leap.bitmask.mail.smtp.gateway import SMTPFactory, LOCAL_FQDN
from leap.bitmask.mail.smtp.gateway import SMTPDelivery

TEST_USER = u'anotheruser@leap.se'


class UnauthenticatedSMTPServer(smtp.SMTP):

    encrypted_only = False

    def __init__(self, outgoing_s, soledad_s, encrypted_only=False):
        smtp.SMTP.__init__(self)

        userid = TEST_USER
        outgoing = outgoing_s[userid]
        avatar = SMTPDelivery(userid, encrypted_only, outgoing)
        self.delivery = avatar

    def validateFrom(self, helo, origin):
        return origin


class UnauthenticatedSMTPFactory(SMTPFactory):
    """
    A Factory that produces a SMTP server that does not authenticate user.
    Only for tests!
    """
    protocol = UnauthenticatedSMTPServer
    domain = LOCAL_FQDN
    encrypted_only = False


def getSMTPFactory(outgoing_s, soledad_s, encrypted_only=False):
    factory = UnauthenticatedSMTPFactory
    factory.encrypted_only = encrypted_only
    proto = factory(outgoing_s, soledad_s).buildProtocol(('127.0.0.1', 0))
    return proto
