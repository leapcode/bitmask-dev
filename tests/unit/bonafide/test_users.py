from mock import patch, ANY

from twisted.internet import defer
from twisted.trial import unittest
from twisted.cred.credentials import UsernamePassword

from leap.bitmask.bonafide.provider import Api
from leap.bitmask.bonafide.session import Session


class UsersTest(unittest.TestCase):

    @patch('leap.bitmask.bonafide.session.Session.is_authenticated')
    @patch('leap.bitmask.bonafide.session.cookieAgentFactory')
    @patch('leap.bitmask.bonafide.session.httpRequest')
    @defer.inlineCallbacks
    def test_recovery_code_creation(self,
                                    mock_http_request,
                                    mock_cookie_agent,
                                    mock_is_authenticated):
        api = Api('https://api.test:4430')
        credentials = UsernamePassword('username', 'password')

        mock_is_authenticated.return_value = True
        session = Session(credentials, api, 'fake path')
        session._uuid = '123'

        response = yield session.update_recovery_code('RECOVERY_CODE')
        mock_http_request.assert_called_with(
            ANY, 'https://api.test:4430/1/users/123',
            method='PUT',
            token=None,
            values={'user[recovery_code_salt]': ANY,
                    'user[recovery_code_verifier]': ANY})
