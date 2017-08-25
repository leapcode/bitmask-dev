# -*- coding: utf-8 -*-
# mail_services.py
# Copyright (C) 2016 LEAP Encryption Acess Project
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
Mail services.

This is quite moving work still.
This should be moved to the different submodules when it stabilizes.
"""
import json
import os
import shutil
import tempfile
from collections import defaultdict
from collections import namedtuple

from twisted.application import service
from twisted.internet import defer
from twisted.logger import Logger

from leap.common.events import catalog, emit_async
from leap.common.files import check_and_fix_urw_only

from leap.bitmask.bonafide import config
from leap.bitmask.hooks import HookableService
from leap.bitmask.util import get_gpg_bin_path, merge_status

try:
    from leap.bitmask.keymanager import KeyManager
    from leap.bitmask.keymanager.errors import KeyNotFound
    from leap.bitmask.keymanager.validation import ValidationLevels
    from leap.bitmask.mail.constants import INBOX_NAME
    from leap.bitmask.mail.mail import Account
    from leap.bitmask.mail.imap import service as imap_service
    from leap.bitmask.mail.smtp import service as smtp_service
    from leap.bitmask.mail.incoming.service import IncomingMail
    from leap.bitmask.mail.incoming.service import INCOMING_CHECK_PERIOD
    from leap.soledad.client.api import Soledad
    HAS_MAIL = True
except ImportError:
    HAS_MAIL = False

try:
    from leap.bitmask.mua import pixelizer
    HAS_MUA = True
except ImportError:
    HAS_MUA = False

from leap.bitmask.core.uuid_map import UserMap
from leap.bitmask.core.configurable import DEFAULT_BASEDIR


class Container(object):

    def __init__(self, service=None):
        self._instances = defaultdict(None)
        if service is not None:
            self.service = service

    def get_instance(self, key):
        return self._instances.get(key, None)

    def add_instance(self, key, data):
        self._instances[key] = data


class ImproperlyConfigured(Exception):
    pass


class SoledadContainer(Container):

    log = Logger()

    def __init__(self, service=None, basedir=DEFAULT_BASEDIR):
        self._basedir = os.path.expanduser(basedir)
        self._usermap = UserMap()
        super(SoledadContainer, self).__init__(service=service)

    def add_instance(self, userid, passphrase, uuid=None, token=None):

        if not uuid:
            bootstrapped_uuid = self._usermap.lookup_uuid(userid, passphrase)
            uuid = bootstrapped_uuid
            if not uuid:
                return
        else:
            self._usermap.add(userid, uuid, passphrase)

        user, provider = userid.split('@')

        soledad_path = os.path.join(self._basedir, 'soledad')
        soledad_url = _get_soledad_uri(self._basedir, provider)
        cert_path = _get_ca_cert_path(self._basedir, provider)

        soledad = self._create_soledad_instance(
            uuid, passphrase, soledad_path, soledad_url,
            cert_path, token)

        super(SoledadContainer, self).add_instance(userid, soledad)

        data = {'user': userid, 'uuid': uuid, 'token': token,
                'soledad': soledad}
        self.service.trigger_hook('on_new_soledad_instance', **data)

        self.log.debug('Syncing soledad for the first time...')
        d = soledad.sync()
        d.addCallbacks(
            lambda _:
            self.service.trigger_hook('on_soledad_first_sync', **data),
            lambda _:
            self.log.failure('Something failed on soledad first sync'))

    def _create_soledad_instance(self, uuid, passphrase, soledad_path,
                                 server_url, cert_file, token):
        # setup soledad info
        secrets_path = os.path.join(soledad_path, '%s.secret' % uuid)
        local_db_path = os.path.join(soledad_path, '%s.db' % uuid)

        return Soledad(
            uuid,
            unicode(passphrase),
            secrets_path=secrets_path,
            local_db_path=local_db_path,
            server_url=server_url,
            cert_file=cert_file,
            auth_token=token)

    def set_remote_auth_token(self, userid, token):
        self.get_instance(userid).token = token

    def sync(self, userid):
        self.get_instance(userid).sync()


def _get_provider_from_full_userid(userid):
    _, provider_id = config.get_username_and_provider(userid)
    # TODO -- this autoconf should be passed from the
    # command flag. workaround to get cli workinf for now.
    return config.Provider(provider_id, autoconf=True)


def is_service_ready(service, provider):
    """
    Returns True when the following conditions are met:
       - Provider offers that service.
       - We have the config files for the service.
       - The service is enabled.
    """
    has_service = provider.offers_service(service)
    has_config = provider.has_config_for_service(service)
    is_enabled = provider.is_service_enabled(service)
    return has_service and has_config and is_enabled


class SoledadService(HookableService):

    log = Logger()

    def __init__(self, basedir):
        service.Service.__init__(self)
        self._basedir = basedir

    def startService(self):
        self.log.info('Starting Soledad Service')
        self._container = SoledadContainer(service=self)
        super(SoledadService, self).startService()

    # hooks

    def hook_on_passphrase_entry(self, **kw):
        userid = kw.get('username')
        provider = _get_provider_from_full_userid(userid)
        provider.callWhenReady(self._hook_on_passphrase_entry, provider, **kw)

    def _hook_on_passphrase_entry(self, provider, **kw):
        if is_service_ready('mx', provider):
            userid = kw.get('username')
            password = kw.get('password')
            uuid = kw.get('uuid')
            container = self._container
            self.log.debug('On_passphrase_entry: '
                           'New Soledad Instance: %s' % userid)
            if not container.get_instance(userid):
                container.add_instance(userid, password, uuid=uuid, token=None)
        else:
            self.log.debug('Service MX is not ready...')

    def hook_on_bonafide_auth(self, **kw):
        userid = kw['username']
        provider = _get_provider_from_full_userid(userid)
        provider.callWhenReady(self._hook_on_bonafide_auth, provider, **kw)

    def _hook_on_bonafide_auth(self, provider, **kw):
        if provider.offers_service('mx'):
            userid = kw['username']
            password = kw['password']
            token = kw['token']
            uuid = kw['uuid']

            container = self._container
            if container.get_instance(userid):
                self.log.debug(
                    'Passing a new SRP Token to Soledad: %s' % userid)
                container.set_remote_auth_token(userid, token)
            else:
                self.log.debug(
                    'Adding a new Soledad Instance: %s' % userid)
                container.add_instance(
                    userid, password, uuid=uuid, token=token)

    def hook_on_passphrase_change(self, **kw):
        # TODO: if bitmask stops before this hook being executed bonafide and
        #       soledad will end up with different passwords
        #       https://leap.se/code/issues/8489
        userid = kw['username']
        password = kw['password']
        soledad = self._container.get_instance(userid)
        if soledad is not None:
            self.log.info('Change soledad passphrase for %s' % userid)
            soledad.change_passphrase(unicode(password))


class KeymanagerContainer(Container):

    log = Logger()

    def __init__(self, service=None, basedir=DEFAULT_BASEDIR):
        self._basedir = os.path.expanduser(basedir)
        self._status = {}
        super(KeymanagerContainer, self).__init__(service=service)

    def add_instance(self, userid, token, uuid, soledad):
        self.log.debug('Adding Keymanager instance for: %s' % userid)
        self._set_status(userid, "starting")
        keymanager = self._create_keymanager_instance(
            userid, token, uuid, soledad)
        super(KeymanagerContainer, self).add_instance(userid, keymanager)

    def set_remote_auth_token(self, userid, token):
        self.get_instance(userid).token = token

    def status(self, userid):
        if userid not in self._status:
            return {'status': 'off', 'error': None, 'keys': None}
        return self._status[userid]

    def get_or_generate_keys(self, userid):
        keymanager = self.get_instance(userid)

        def _found_key(key):
            self.log.info('Found key: %r' % key)
            self._set_status(userid, "on", keys="found")
            return key

        def key_generated_cb(passthru):
            self._set_status(userid, "on", keys="found")
            return passthru

        def _if_not_found_generate(failure):
            failure.trap(KeyNotFound)
            self.log.info('Key not found, generating key for %s' % (userid,))
            self._set_status(userid, "starting", keys="generating")
            d = keymanager.gen_key()
            d.addCallback(key_generated_cb)
            d.addErrback(_log_key_error)
            return d

        def _log_key_error(failure):
            self.log.failure('Error while generating key!')
            error = "Error generating key: %s" % failure.getErrorMessage()
            self._set_status(userid, "failed", error=error)
            return failure

        self.log.info('Looking up private key for %s' % userid)
        d = keymanager.get_key(userid, private=True, fetch_remote=False)
        d.addCallbacks(_found_key, _if_not_found_generate)
        d.addCallback(self._on_keymanager_ready_cb, keymanager, userid)
        return d

    @defer.inlineCallbacks
    def send_if_outdated_key_in_nicknym(self, userid):
        keymanager = self.get_instance(userid)
        key = yield keymanager.get_key(userid, fetch_remote=False)
        try:
            remote = yield keymanager._nicknym.fetch_key_with_address(userid)
        except Exception:
            remote = {}

        if (keymanager.OPENPGP_KEY not in remote or
                key.key_data != remote[KeyManager.OPENPGP_KEY]):
            yield keymanager.send_key()

    def _set_status(self, address, status, error=None, keys=None):
        self._status[address] = {"status": status,
                                 "error": error, "keys": keys}
        emit_async(catalog.MAIL_STATUS_CHANGED, address)

    def _on_keymanager_ready_cb(self, key, keymanager, userid):
        soledad = keymanager._soledad
        data = {'userid': userid, 'soledad': soledad, 'keymanager': keymanager}
        self.service.trigger_hook('on_new_keymanager_instance', **data)
        return key

    def _create_keymanager_instance(self, userid, token, uuid, soledad):
        user, provider = userid.split('@')
        nickserver_uri = self._get_nicknym_uri(provider)

        cert_path = _get_ca_cert_path(self._basedir, provider)
        api_uri = self._get_api_uri(provider)

        if not token:
            token = self.service.tokens.get(userid)

        km_args = (userid, nickserver_uri, soledad)

        km_kwargs = {
            "token": token, "uid": uuid,
            "api_uri": api_uri, "api_version": "1",
            "ca_cert_path": cert_path,
            "gpgbinary": get_gpg_bin_path()
        }
        keymanager = KeyManager(*km_args, **km_kwargs)
        return keymanager

    def _get_api_uri(self, provider):
        api_uri = config.Provider(provider).api_uri
        return api_uri

    def _get_nicknym_uri(self, provider):
        return 'https://nicknym.{provider}:6425'.format(
            provider=provider)


class KeymanagerService(HookableService):

    log = Logger()

    def __init__(self, basedir=DEFAULT_BASEDIR):
        service.Service.__init__(self)
        self._basedir = basedir
        self._container = None

    def startService(self):
        self.log.debug('Starting Keymanager Service')
        self._container = KeymanagerContainer(self._basedir)
        self._container.service = self
        self.tokens = {}
        super(KeymanagerService, self).startService()

    # hooks

    def hook_on_new_soledad_instance(self, **kw):
        container = self._container
        user = kw['user']
        token = kw['token']
        uuid = kw['uuid']
        soledad = kw['soledad']
        if not container.get_instance(user):
            self.log.debug('Adding a new Keymanager instance for %s' % user)
            if not token:
                token = self.tokens.get(user)
            container.add_instance(user, token, uuid, soledad)

    def hook_on_soledad_first_sync(self, **kw):
        userid = kw['user']
        d = self._container.get_or_generate_keys(userid)
        d.addCallback(
            lambda _: self._container.send_if_outdated_key_in_nicknym(userid))

    def hook_on_bonafide_auth(self, **kw):
        userid = kw['username']
        provider = _get_provider_from_full_userid(userid)
        provider.callWhenReady(self._hook_on_bonafide_auth, provider, **kw)

    def _hook_on_bonafide_auth(self, provider, **kw):
        if provider.offers_service('mx'):
            userid = kw['username']
            token = kw['token']

            container = self._container
            if container.get_instance(userid):
                self.log.debug(
                    'Passing a new SRP Token '
                    'to Keymanager: %s' % userid)
                container.set_remote_auth_token(userid, token)
            else:
                self.log.debug('Storing the keymanager token... %s ' % token)
                self.tokens[userid] = token

    # commands

    def do_list_keys(self, userid, private=False):
        km = self._container.get_instance(userid)
        if km is None:
            return defer.fail(ValueError("User " + userid + " has no active "
                                         "keymanager"))

        d = km.get_all_keys(private=private)
        d.addCallback(lambda keys: [dict(key) for key in keys])
        return d

    def do_export(self, userid, address, private=False, fetch_remote=False):
        km = self._container.get_instance(userid)
        if km is None:
            return defer.fail(ValueError("User " + userid + " has no active "
                                         "keymanager"))

        d = km.get_key(address, private=private, fetch_remote=fetch_remote)
        d.addCallback(lambda key: dict(key))
        return d

    def do_insert(self, userid, address, rawkey, validation='Fingerprint'):
        km = self._container.get_instance(userid)
        if km is None:
            return defer.fail(ValueError("User " + userid + " has no active "
                                         "keymanager"))

        validation = ValidationLevels.get(validation)
        d = km.put_raw_key(rawkey, address, validation=validation)
        d.addCallback(lambda _: km.get_key(address, fetch_remote=False))
        d.addCallback(lambda key: dict(key))
        return d

    @defer.inlineCallbacks
    def do_delete(self, userid, address, private=False):
        km = self._container.get_instance(userid)
        if km is None:
            raise ValueError("User " + userid + " has no active keymanager")

        key = yield km.get_key(address, private=private, fetch_remote=False)
        km.delete_key(key)
        defer.returnValue(key.fingerprint)

    def status(self, userid):
        return self._container.status(userid)


class StandardMailService(service.MultiService, HookableService):
    """
    A collection of Services.

    This is the parent service, that launches 3 different services that expose
    Encrypted Mail Capabilities on specific ports:

        - SMTP service, on port 2013
        - IMAP service, on port 1984
        - The IncomingMail Service, which doesn't listen on any port, but
          watches and processes the Incoming Queue and saves the processed mail
          into the matching INBOX.
    """

    name = 'mail'
    log = Logger()

    # TODO factor out Mail Service to inside mail package.

    def __init__(self, basedir, mixnet_enabled=False):
        self._basedir = basedir
        self._soledad_sessions = {}
        self._keymanager_sessions = {}
        self._sendmail_opts = {}
        self._service_tokens = {}
        self._mixnet_enabled = mixnet_enabled
        super(StandardMailService, self).__init__()
        self.initializeChildrenServices()

    def initializeChildrenServices(self):
        self.addService(IMAPService(self._soledad_sessions))
        self.addService(SMTPService(
            self._soledad_sessions, self._keymanager_sessions,
            self._sendmail_opts))
        # TODO adapt the service to receive soledad/keymanager sessions object.
        # See also the TODO before IncomingMailService.startInstance
        self.addService(IncomingMailService(self))

    def startService(self):
        self.log.info('Starting Mail Service')
        super(StandardMailService, self).startService()

    def stopService(self):
        self.log.info('Stopping Mail service')
        super(StandardMailService, self).stopService()

    def startInstance(self, userid, soledad, keymanager):
        username, provider = userid.split('@')

        self._soledad_sessions[userid] = soledad
        self._keymanager_sessions[userid] = keymanager

        sendmail_opts = _get_sendmail_opts(self._basedir, provider, username)
        self._sendmail_opts[userid] = sendmail_opts

        def registerToken(token):
            self._service_tokens[userid] = token
            return token

        incoming = self.getServiceNamed('incoming_mail')
        d = incoming.startInstance(userid)
        d.addCallback(
            lambda _: soledad.get_or_create_service_token('mail_auth'))
        d.addCallback(registerToken)
        d.addCallback(self._write_tokens_file, userid)
        d.addCallback(
            self._maybe_start_pixelated, userid, soledad, keymanager)
        return d

    # hooks

    def hook_on_new_keymanager_instance(self, **kw):
        # XXX we can specify this as a waterfall, or just AND the two
        # conditions.
        userid = kw['userid']
        soledad = kw['soledad']
        keymanager = kw['keymanager']

        # TODO --- only start instance if "autostart" is True.
        self.startInstance(userid, soledad, keymanager)

    @defer.inlineCallbacks
    def hook_on_bonafide_auth(self, **kw):
        userid = kw['username']
        self._maybe_start_incoming_service(userid)
        # TODO: if it's expired we should renew it
        yield self._maybe_fetch_smtp_certificate(userid)

    def _maybe_start_incoming_service(self, userid):
        """
        try to turn on incoming mail service for the user that just logged in
        """
        self.log.debug(
            'Looking for incoming mail service for auth: %s' % userid)
        multiservice = self.getServiceNamed('incoming_mail')
        try:
            incoming = multiservice.getServiceNamed(userid)
            incoming.startService()
        except KeyError:
            self.log.debug('No incoming service for %s' % userid)

    @defer.inlineCallbacks
    def _maybe_fetch_smtp_certificate(self, userid):
        # check if smtp cert exists
        username, provider = userid.split('@')
        cert_path = _get_smtp_client_cert_path(self._basedir, provider,
                                               username)
        if os.path.exists(cert_path):
            defer.returnValue(None)

        # fetch smtp cert and store
        bonafide = self.parent.getServiceNamed("bonafide")
        _, cert_str = yield bonafide.do_get_smtp_cert(userid)

        cert_dir = os.path.dirname(cert_path)
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir, mode=0700)
        with open(cert_path, 'w') as outf:
            outf.write(cert_str)
        check_and_fix_urw_only(cert_path)

    def hook_on_bonafide_logout(self, **kw):
        username = kw.get('username', None)
        if username:
            multiservice = self.getServiceNamed('incoming_mail')
            try:
                incoming = multiservice.getServiceNamed(username)
            except KeyError:
                incoming = None
            if incoming:
                self.log.debug(
                    'looking for incoming mail service '
                    'for logout: %s' % username)
                incoming.stopService()

    # commands

    @defer.inlineCallbacks
    def do_status(self, userid):
        smtp = self.getServiceNamed('smtp')
        imap = self.getServiceNamed('imap')
        keymanager = self.parent.getServiceNamed('keymanager')
        incoming = self.getServiceNamed('incoming_mail')
        incoming_status = yield incoming.status(userid)
        childrenStatus = {
            'smtp': smtp.status(),
            'imap': imap.status(),
            'keymanager': keymanager.status(userid),
            'incoming': incoming_status
        }
        defer.returnValue(merge_status(childrenStatus))

    def do_mixnet_status(self, userid, address):
        # XXX: for now there is no support in the provider
        #      we'll mock it if it's enabled
        provider = address.split('@')[1]
        if not self._mixnet_enabled:
            status = 'disabled'
        elif provider in ['panoramix-project.eu', 'riseup.net']:
            status = 'ok'
        else:
            status = 'unsuported'
        return {'status': status}

    def get_token(self, userid):
        token = self._service_tokens.get(userid)
        return {'user': userid, 'token': token}

    def do_add_msg(self, userid, raw_msg, mailbox=None):
        if not mailbox:
            mailbox = INBOX_NAME

        account = self._get_account(userid)
        d = account.get_collection_by_mailbox(mailbox)
        d.addCallback(lambda collection: collection.add_msg(raw_msg))
        d.addCallback(lambda _: {'added': True})
        return d

    # access to containers

    def get_soledad_session(self, userid):
        return self._soledad_sessions.get(userid)

    def get_keymanager_session(self, userid):
        return self._keymanager_sessions.get(userid)

    # other helpers

    def _write_tokens_file(self, token, userid):
        tokens_folder = os.path.join(tempfile.gettempdir(), "bitmask_tokens")
        if os.path.exists(tokens_folder):
            try:
                shutil.rmtree(tokens_folder)
            except OSError as e:
                self.log.warn("Can't remove tokens folder %s: %s"
                              % (tokens_folder, e))
                return
        os.mkdir(tokens_folder, 0700)

        tokens_path = os.path.join(tokens_folder,
                                   "%s.json" % (userid,))
        token_dict = {'mail_auth': self._service_tokens[userid]}
        with open(tokens_path, 'w') as ftokens:
            json.dump(token_dict, ftokens)

    def _maybe_start_pixelated(self, passthrough, userid, soledad, keymanager):
        account = self._get_account(userid)
        if HAS_MUA and pixelizer.HAS_PIXELATED:
            pixelizer.start_pixelated_user_agent(
                userid, soledad, keymanager, account)
        return passthrough

    def _get_account(self, userid):
        incoming = self.getServiceNamed('incoming_mail')
        return incoming.getServiceNamed(userid).account


class IMAPService(service.Service):

    name = 'imap'
    log = Logger()

    def __init__(self, soledad_sessions):
        self._soledad_sessions = soledad_sessions
        self._port = None
        self._factory = None
        super(IMAPService, self).__init__()

    def startService(self):
        if not HAS_MAIL:
            self.log.info('Mail module not found')
            return
        self.log.info('Starting IMAP Service')
        port, factory = imap_service.run_service(
            self._soledad_sessions, factory=self._factory)
        self._port = port
        self._factory = factory
        super(IMAPService, self).startService()

    def stopService(self):
        self.log.info('Stopping IMAP Service')
        if self._port:
            self._port.stopListening()
            self._port = None
        if self._factory:
            self._factory.doStop()
        super(IMAPService, self).stopService()

    def status(self):
        return {
            'status': 'on' if self.running else 'off',
            'error': None
        }


class SMTPService(service.Service):

    name = 'smtp'
    log = Logger()

    def __init__(self, soledad_sessions, keymanager_sessions, sendmail_opts,
                 basedir=DEFAULT_BASEDIR):

        self._basedir = os.path.expanduser(basedir)
        self._soledad_sessions = soledad_sessions
        self._keymanager_sessions = keymanager_sessions
        self._sendmail_opts = sendmail_opts
        self._port = None
        self._factory = None
        super(SMTPService, self).__init__()

    def startService(self):
        if not HAS_MAIL:
            self.log.info('Mail module not found')
            return
        self.log.info('starting smtp service')
        port, factory = smtp_service.run_service(
            self._soledad_sessions,
            self._keymanager_sessions,
            self._sendmail_opts,
            factory=self._factory)
        self._port = port
        self._factory = factory
        super(SMTPService, self).startService()

    def stopService(self):
        self.log.info('Stopping SMTP Service')
        if self._port:
            self._port.stopListening()
            self._port = None
        if self._factory:
            self._factory.doStop()
        super(SMTPService, self).stopService()

    def status(self):
        return {
            'status': 'on' if self.running else 'off',
            'error': None
        }


class IncomingMailService(service.MultiService):
    """
    Manage child services that check for incoming mail for individual users.
    """

    name = 'incoming_mail'
    log = Logger()

    def __init__(self, mail_service):
        super(IncomingMailService, self).__init__()
        self._mail = mail_service
        self._status = {}

    def startService(self):
        self.log.info('Starting Incoming Mail Service')
        super(IncomingMailService, self).startService()

    def stopService(self):
        super(IncomingMailService, self).stopService()

    # Individual accounts

    def startInstance(self, userid):
        """returns: a deferred"""
        self._set_status(userid, "starting")
        soledad = self._mail.get_soledad_session(userid)
        keymanager = self._mail.get_keymanager_session(userid)

        self.log.info('Setting up Incoming Mail Service for %s' % userid)
        return self._start_incoming_mail_instance(
            keymanager, soledad, userid)

    @defer.inlineCallbacks
    def status(self, userid):
        if userid not in self._status:
            defer.returnValue({'status': 'off', 'error': None, 'unread': None})

        status = self._status[userid]
        incoming = self.getServiceNamed(userid)
        if status['status'] == 'on':
            status['unread'] = yield incoming.unread()
        defer.returnValue(status)

    def _set_status(self, address, status, error=None, unread=None):
        self._status[address] = {"status": status, "error": error,
                                 "unread": unread}
        emit_async(catalog.MAIL_STATUS_CHANGED, address)

    def _start_incoming_mail_instance(self, keymanager, soledad,
                                      userid, start_sync=True):

        def setUpIncomingMail(inbox, acc):
            incoming_mail = IncomingMail(
                keymanager, soledad,
                inbox, userid,
                check_period=INCOMING_CHECK_PERIOD)
            incoming_mail.account = acc
            self.log.debug('Setting Incoming Mail Service for %s' % userid)
            incoming_mail.setName(userid)
            self.addService(incoming_mail)

        def setStatusOn(res):
            self._set_status(userid, "on")
            return res

        # XXX ----------------------------------------------------------------
        # TODO we probably want to enforce a SINGLE ACCOUNT INSTANCE
        # earlier in the bootstrap process (ie, upper in the hierarchy of
        # services) so that the single instance can be shared by the imap and
        # the pixelated mua.
        # XXX ----------------------------------------------------------------

        acc = Account(soledad, userid)
        d = acc.callWhenReady(
            lambda _: acc.get_collection_by_mailbox(INBOX_NAME))
        d.addCallback(setUpIncomingMail, acc)
        d.addCallback(setStatusOn)
        d.addErrback(self._errback, userid)
        return d

    def _errback(self, failure, userid):
        self._set_status(userid, "failed", error=str(failure))
        self.log.failure('failed!')

# --------------------------------------------------------------------
#
# config utilities. should be moved to bonafide
#


SERVICES = ('soledad', 'smtp', 'vpn')


Provider = namedtuple(
    'Provider', ['hostname', 'ip_address', 'location', 'port'])

SendmailOpts = namedtuple(
    'SendmailOpts', ['cert', 'key', 'hostname', 'port'])


def _get_ca_cert_path(basedir, provider):
    path = os.path.join(
        basedir, 'providers', provider, 'keys', 'ca', 'cacert.pem')
    return path


def _get_sendmail_opts(basedir, provider, username):
    cert = _get_smtp_client_cert_path(basedir, provider, username)
    key = cert
    prov = _get_provider_for_service('smtp', basedir, provider)
    hostname = prov.hostname
    port = prov.port
    opts = SendmailOpts(cert, key, hostname, port)
    return opts


def _get_smtp_client_cert_path(basedir, provider, username):
    path = os.path.join(
        basedir, 'providers', provider, 'keys', 'client', 'smtp_%s.pem' %
        username)
    return path


def _get_config_for_service(service, basedir, provider):
    if service not in SERVICES:
        raise ImproperlyConfigured('Tried to use an unknown service')

    config_path = os.path.join(
        basedir, 'providers', provider, '%s-service.json' % service)
    try:
        with open(config_path) as config:
            config = json.loads(config.read())
    except IOError:
        # FIXME might be that the provider DOES NOT offer this service!
        raise ImproperlyConfigured(
            'could not open config file %s' % config_path)
    else:
        return config


def first(xs):
    return xs[0]


def _pick_server(config, strategy=first):
    """
    Picks a server from a list of possible choices.
    The service files have a  <describe>.
    This implementation just picks the FIRST available server.
    """
    servers = config['hosts'].keys()
    choice = config['hosts'][strategy(servers)]
    return choice


def _get_subdict(d, keys):
    return {key: d.get(key) for key in keys}


def _get_provider_for_service(service, basedir, provider):

    if service not in SERVICES:
        raise ImproperlyConfigured('Tried to use an unknown service')

    config = _get_config_for_service(service, basedir, provider)
    p = _pick_server(config)
    attrs = _get_subdict(p, ('hostname', 'ip_address', 'location', 'port'))
    provider = Provider(**attrs)
    return provider


def _get_smtp_uri(basedir, provider):
    prov = _get_provider_for_service('smtp', basedir, provider)
    url = 'https://{hostname}:{port}'.format(
        hostname=prov.hostname, port=prov.port)
    return url


def _get_soledad_uri(basedir, provider):
    prov = _get_provider_for_service('soledad', basedir, provider)
    url = 'https://{hostname}:{port}'.format(
        hostname=prov.hostname, port=prov.port)
    return url
