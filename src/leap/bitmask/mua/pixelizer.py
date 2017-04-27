# -*- coding: utf-8 -*-
# pixelizer.py
# Copyright (C) 2016-2017 LEAP
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
Pixelizer: the pixelated integrator.

Right now this module is kind of hardcoded, but it should be possible for
bitmask to use this as an optional plugin. For the moment we fail gracefully if
we cannot find the pixelated modules in the import path.

There's a lot of code duplication right now in this double game of adaptors for
pixelated adaptors. Refactoring pixelated and bitmask should be possible so
that we converge the mail apis and stop needing this nasty proliferation of
adaptors.

However, some care has to be taken to avoid certain types of concurrency bugs.
"""

import json
import os
import sys

from twisted.internet import defer, reactor
from twisted.logger import Logger

from leap.common.config import get_path_prefix
from leap.bitmask.keymanager import KeyNotFound

try:
    from pixelated.adapter.mailstore import LeapMailStore
    from pixelated.application import SingleUserServicesFactory
    from pixelated.application import UserAgentMode
    from pixelated.application import start_site
    from pixelated.bitmask_libraries.smtp import LeapSMTPConfig
    from pixelated.config.sessions import SessionCache
    from pixelated.config import services
    from pixelated.resources.root_resource import RootResource
    import pixelated_www
    HAS_PIXELATED = True
except ImportError as exc:
    HAS_PIXELATED = False


log = Logger()


# TODO
# [ ] pre-authenticate


def start_pixelated_user_agent(userid, soledad, keymanager, account):

    try:
        leap_session = LeapSessionAdapter(
            userid, soledad, keymanager, account)
    except Exception as exc:
        log.error("Got error! %r" % exc)

    config = Config()
    leap_home = os.path.join(get_path_prefix(), 'leap')
    config.leap_home = leap_home
    leap_session.config = config

    services_factory = SingleUserServicesFactory(
        UserAgentMode(is_single_user=True))

    if getattr(sys, 'frozen', False):
        # we are running in a |PyInstaller| bundle
        static_folder = os.path.join(sys._MEIPASS, 'pixelated_www')
    else:
        static_folder = os.path.abspath(pixelated_www.__path__[0])

    resource = RootResource(services_factory, static_folder=static_folder)

    config.host = 'localhost'
    config.port = 9090
    config.sslkey = None
    config.sslcert = None
    config.manhole = False

    d = leap_session.account.callWhenReady(
        lambda _: _start_in_single_user_mode(
            leap_session, config,
            resource, services_factory))
    return d


def get_smtp_config(provider):
    config_path = os.path.join(
        get_path_prefix(), 'leap', 'providers', provider, 'smtp-service.json')
    json_config = json.loads(open(config_path).read())
    chosen_host = json_config['hosts'].keys()[0]
    hostname = json_config['hosts'][chosen_host]['hostname']
    port = json_config['hosts'][chosen_host]['port']

    config = Config()
    config.host = hostname
    config.port = port
    return config


class NickNym(object):

    def __init__(self, keymanager, userid):
        self._email = userid
        self.keymanager = keymanager

    @defer.inlineCallbacks
    def generate_openpgp_key(self):
        key_present = yield self._key_exists(self._email)
        if not key_present:
            yield self._gen_key()
        yield self._send_key_to_leap()

    @defer.inlineCallbacks
    def _key_exists(self, email):
        try:
            yield self.fetch_key(email, private=True, fetch_remote=False)
            defer.returnValue(True)
        except KeyNotFound:
            defer.returnValue(False)

    def fetch_key(self, email, private=False, fetch_remote=True):
        return self.keymanager.get_key(
            email, private=private, fetch_remote=fetch_remote)

    def get_key(self, *args, **kw):
        return self.keymanager.get_key(*args, **kw)

    def _gen_key(self):
        return self.keymanager.gen_key()

    def _send_key_to_leap(self):
        return self.keymanager.send_key()


class _LeapMailStore(LeapMailStore):

    def __init__(self, soledad, account):
        self.account = account
        super(_LeapMailStore, self).__init__(soledad)

    # We should rewrite the LeapMailStore in the coming pixelated fork so that
    # we reuse the account instance.
    @defer.inlineCallbacks
    def add_mail(self, mailbox_name, raw_msg):
        inbox = yield self.account.get_collection_by_mailbox(mailbox_name)
        yield inbox.add_msg(raw_msg, ('\\Recent',), notify_just_mdoc=False)


class LeapSessionAdapter(object):

    def __init__(self, userid, soledad, keymanager, account):

        self.userid = userid
        self.soledad = soledad

        # XXX this needs to be converged with our public apis.
        _n = NickNym(keymanager, userid)
        self.nicknym = self.keymanager = _n

        self.mail_store = _LeapMailStore(soledad, account)

        self.account = account

        self.user_auth = Config()
        self.user_auth.uuid = soledad.uuid

        self.fresh_account = False
        self.incoming_mail_fetcher = None

        username, provider = userid.split('@')
        smtp_client_cert = os.path.join(
            get_path_prefix(),
            'leap', 'providers', provider, 'keys',
            'client',
            'smtp_{username}.pem'.format(
                username=username))

        _prov = Config()
        _prov.server_name = provider
        self.provider = _prov

        assert(os.path.isfile(smtp_client_cert))

        smtp_config = get_smtp_config(provider)
        smtp_host = smtp_config.host
        smtp_port = smtp_config.port

        self.smtp_config = LeapSMTPConfig(
            userid,
            smtp_client_cert, smtp_host, smtp_port)

    def account_email(self):
        return self.userid

    def close(self):
        pass

    @property
    def is_closed(self):
        return self._is_closed

    def remove_from_cache(self):
        key = SessionCache.session_key(self.provider, self.userid)
        SessionCache.remove_session(key)

    def sync(self):
        return self.soledad.sync()


class Config(object):
    pass


def _start_in_single_user_mode(leap_session, config, resource,
                               services_factory):
    start_site(config, resource)
    reactor.callLater(
        0, start_user_agent_in_single_user_mode,
        resource, services_factory,
        leap_session.config.leap_home, leap_session)


@defer.inlineCallbacks
def start_user_agent_in_single_user_mode(root_resource,
                                         services_factory,
                                         leap_home, leap_session):
    log.info('Pixelated bootstrap done, loading services for user %s'
             % leap_session.user_auth.uuid)
    _services = services.Services(leap_session)
    yield _services.setup()

    # TODO we might want to use a Bitmask specific mail
    # if leap_session.fresh_account:
    #   yield add_welcome_mail(leap_session.mail_store)

    services_factory.add_session(leap_session.user_auth.uuid, _services)
    root_resource.initialize(provider=leap_session.provider)
    log.info('Done, the Pixelated User Agent is ready to be used')
