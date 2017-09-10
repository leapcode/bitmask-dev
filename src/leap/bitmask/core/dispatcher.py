# -*- coding: utf-8 -*-
# dispatcher.py
# Copyright (C) 2016 LEAP
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
Command dispatcher.
"""
import json

try:
    from Queue import Queue
except ImportError:
    from queue import Queue

from twisted.internet import defer
from twisted.python import failure
from twisted.logger import Logger

from leap.common.events import register_async as register
from leap.common.events import unregister_async as unregister
from leap.common.events import catalog

from .api import APICommand, register_method


log = Logger()


class DispatchError(Exception):
    pass


class SubCommand(object):

    __metaclass__ = APICommand

    def dispatch(self, service, *parts, **kw):
        subcmd = ''
        try:
            subcmd = parts[1]
            _method = getattr(self, 'do_' + subcmd.upper(), None)
        except IndexError:
            raise RuntimeError('Can\'t dispatch subcommand: %s' % str(subcmd))

        if not _method:
            raise RuntimeError('No such subcommand: ' + subcmd)
        return defer.maybeDeferred(_method, service, *parts, **kw)


class BonafideCmd(SubCommand):

    label = 'bonafide'

    def __init__(self):
        self.subcommand_user = UserCmd()
        self.subcommand_provider = ProviderCmd()

    def do_USER(self, bonafide, *parts):
        return self.subcommand_user.dispatch(bonafide, *parts[1:])

    def do_PROVIDER(self, bonafide, *parts):
        return self.subcommand_provider.dispatch(bonafide, *parts[1:])


class ProviderCmd(SubCommand):

    label = 'bonafide.provider'

    @register_method("{'domain': str, 'api_uri': str, 'api_version': str}")
    def do_CREATE(self, bonafide, *parts):
        domain = parts[2]
        return bonafide.do_provider_create(domain)

    @register_method("{'domain': str, 'api_uri': str, 'api_version': str}")
    def do_READ(self, bonafide, *parts):
        domain = parts[2]
        service = None
        if len(parts) > 3:
            service = parts[3]
        return bonafide.do_provider_read(domain, service)

    @register_method("")
    def do_DELETE(self, bonafide, *parts):
        domain = parts[2]
        return bonafide.do_provider_delete(domain)

    @register_method("[{'domain': str}]")
    def do_LIST(self, bonafide, *parts):
        seeded = False
        if len(parts) > 2:
            seeded = parts[2]
        return bonafide.do_provider_list(seeded)


class UserCmd(SubCommand):

    label = 'bonafide.user'

    @register_method("{'srp_token': unicode, 'uuid': unicode}")
    def do_AUTHENTICATE(self, bonafide, *parts):
        try:
            user, password = parts[2], parts[3]
        except IndexError:
            raise DispatchError(
                'wrong number of arguments: expected 2 or 3, got %s' % (
                    len(parts[2:])))
        autoconf = False
        if len(parts) > 4:
            if parts[4] == 'True':
                autoconf = True

        d = defer.maybeDeferred(
            bonafide.do_authenticate, user, password, autoconf)
        return d

    @register_method("{'signup': 'ok', 'user': str}")
    def do_CREATE(self, bonafide, *parts):
        if len(parts) < 5:
            raise DispatchError(
                'wrong number of arguments: expected min 3, got %s' % (
                    len(parts[2:])))

        # params are: [user, create, full_id, password, invite, autoconf]
        user, password, invite = parts[2], parts[3], parts[4]

        # TODO factor out null/bool conversion to a util function.
        if invite == 'none':
            invite = None
        autoconf = False
        if len(parts) > 5:
            if parts[5] == 'True':
                autoconf = True
        return bonafide.do_signup(user, password, invite, autoconf)

    @register_method("{'logout': 'ok'}")
    def do_LOGOUT(self, bonafide, *parts):
        try:
            user = parts[2]
        except IndexError:
            raise DispatchError(
                'wrong number of arguments: expected 1, got %s' % (
                    len(parts[2:])))
        return bonafide.do_logout(user)

    @register_method("[{'userid': str, 'authenticated': bool}]")
    def do_LIST(self, bonafide, *parts):
        return bonafide.do_list_users()

    @register_method("{'update': 'ok'}")
    def do_UPDATE(self, bonafide, *parts):
        try:
            user, current_password, new_password = parts[2], parts[3], parts[4]
        except IndexError:
            raise DispatchError(
                'wrong number of arguments: expected 3, got %s' % (
                    len(parts[2:])))
        return bonafide.do_change_password(
            user, current_password, new_password)


class VPNCmd(SubCommand):

    label = 'vpn'

    @register_method('dict')
    def do_ENABLE(self, service, *parts):
        d = service.do_enable_service(self.label)
        return d

    @register_method('dict')
    def do_DISABLE(self, service, *parts):
        d = service.do_disable_service(self.label)
        return d

    @register_method('dict')
    def do_STATUS(self, vpn, *parts):
        result = vpn.do_status()
        return result

    @register_method('dict')
    def do_START(self, vpn, *parts):
        try:
            provider = parts[2]
        except IndexError:
            provider = None
        d = vpn.start_vpn(provider)
        return d

    @register_method('dict')
    def do_STOP(self, vpn, *parts):
        d = vpn.stop_vpn()
        return d

    @register_method('dict')
    def do_CHECK(self, vpn, *parts):
        try:
            provider = parts[2]
        except IndexError:
            provider = None
        d = vpn.do_check(provider)
        return d

    @register_method('dict')
    def do_GET_CERT(self, vpn, *parts):
        try:
            username = parts[2]
        except IndexError:
            raise DispatchError(
                'wrong number of arguments: expected 1, got none')
        d = vpn.do_get_cert(username)
        return d

    @register_method('dict')
    def do_INSTALL(self, vpn, *parts):
        d = vpn.do_install()
        return d

    @register_method('dict')
    def do_UNINSTALL(self, vpn, *parts):
        d = vpn.do_uninstall()
        return d

    @register_method('dict')
    def do_LIST(self, vpn, *parts):
        d = vpn.do_list()
        return d

    @register_method('list')
    def do_LOCATIONS(self, vpn, *parts):
        if len(parts) > 2:
            return vpn.do_set_locations(parts[2:])

        return vpn.do_get_locations()

    @register_method('list')
    def do_COUNTRIES(self, vpn, *parts):
        if len(parts) > 2:
            return vpn.do_set_countries(parts[2:])

        return vpn.do_get_countries()


class MailCmd(SubCommand):

    label = 'mail'

    @register_method('dict')
    def do_ENABLE(self, service, *parts, **kw):
        d = service.do_enable_service(self.label)
        return d

    @register_method('dict')
    def do_DISABLE(self, service, *parts, **kw):
        d = service.do_disable_service(self.label)
        return d

    @register_method('dict')
    def do_STATUS(self, mail, *parts, **kw):
        try:
            userid = parts[2]
        except IndexError:
            raise DispatchError(
                'wrong number of arguments: expected 1, got none')
        d = mail.do_status(userid)
        return d

    @register_method('dict')
    def do_GET_TOKEN(self, mail, *parts, **kw):
        try:
            userid = parts[2]
        except IndexError:
            raise DispatchError(
                'wrong number of arguments: expected 1, got none')
        return mail.get_token(userid)

    @register_method('dict')
    def do_MIXNET_STATUS(self, mail, *parts, **kw):
        try:
            userid = parts[2]
            address = parts[3]
        except IndexError:
            raise DispatchError(
                'wrong number of arguments: expected 2')
        d = mail.do_mixnet_status(userid, address)
        return d

    @register_method('dict')
    def do_ADD_MSG(self, mail, *parts, **kw):
        try:
            userid = parts[2]
            mailbox = parts[3]
            msg = parts[4]
        except IndexError:
            raise DispatchError(
                'wrong number of arguments: expected 3, got none')
        d = mail.do_add_msg(userid, msg, mailbox)
        return d


class WebUICmd(SubCommand):

    label = 'web'

    @register_method('dict')
    def do_ENABLE(self, service, *parts, **kw):
        d = service.do_enable_service(self.label)
        return d

    @register_method('dict')
    def do_DISABLE(self, service, *parts, **kw):
        d = service.do_disable_service(self.label)
        return d

    @register_method('dict')
    def do_STATUS(self, webui, *parts, **kw):
        d = webui.do_status()
        return d


class KeysCmd(SubCommand):

    label = 'keys'

    @register_method("[dict]")
    def do_LIST(self, service, *parts, **kw):
        if len(parts) < 3:
            raise ValueError("A uid is needed")
        uid = parts[2]

        private = False
        if parts[-1] == 'private':
            private = True

        return service.do_list_keys(uid, private)

    @register_method('dict')
    def do_EXPORT(self, service, *parts, **kw):
        if len(parts) < 4:
            raise ValueError("An email address is needed")
        uid = parts[2]
        address = parts[3]

        private = False
        fetch_remote = False
        if len(parts) > 4:
            if parts[4] == 'private':
                private = True
            elif parts[4] == 'fetch':
                fetch_remote = True

        return service.do_export(uid, address, private, fetch_remote)

    @register_method('dict')
    def do_INSERT(self, service, *parts, **kw):
        if len(parts) < 6:
            raise ValueError("An email address is needed")
        uid = parts[2]
        address = parts[3]
        validation = parts[4]
        rawkey = parts[5]

        return service.do_insert(uid, address, rawkey, validation)

    @register_method('str')
    def do_DELETE(self, service, *parts, **kw):
        if len(parts) < 4:
            raise ValueError("An email address is needed")
        uid = parts[2]
        address = parts[3]

        private = False
        if parts[-1] == 'private':
            private = True

        return service.do_delete(uid, address, private)


class EventsCmd(SubCommand):

    label = 'events'

    def __init__(self):
        self.queue = Queue()
        self.waiting = []

    @register_method("")
    def do_REGISTER(self, _, *parts, **kw):
        event = getattr(catalog, parts[2])
        register(event, self._callback)

    @register_method("")
    def do_UNREGISTER(self, _, *parts, **kw):
        event = getattr(catalog, parts[2])
        unregister(event)

    @register_method("(str, [])")
    def do_POLL(self, _, *parts, **kw):
        if not self.queue.empty():
            return self.queue.get()

        d = defer.Deferred()
        self.waiting.append(d)
        return d

    def _callback(self, event, *content):
        payload = (str(event), content)
        if not self.waiting:
            self.queue.put(payload)
            return

        while self.waiting:
            d = self.waiting.pop()
            d.callback(payload)


class CoreCmd(SubCommand):

    label = 'core'

    @register_method("{'mem_usage': str}")
    def do_STATS(self, core, *parts):
        return core.do_stats()

    @register_method("{version_core': '0.0.0'}")
    def do_VERSION(self, core, *parts):
        return core.do_version()

    @register_method("{'mail': 'running'}")
    def do_STATUS(self, core, *parts):
        return core.do_status()

    @register_method("{'stop': 'ok'}")
    def do_STOP(self, core, *parts):
        return core.do_stop()


class CommandDispatcher(object):

    __metaclass__ = APICommand

    def __init__(self, core):

        self.core = core
        self.subcommand_core = CoreCmd()
        self.subcommand_bonafide = BonafideCmd()
        self.subcommand_vpn = VPNCmd()
        self.subcommand_mail = MailCmd()
        self.subcommand_keys = KeysCmd()
        self.subcommand_events = EventsCmd()
        self.subcommand_webui = WebUICmd()

    def do_CORE(self, *parts):
        d = self.subcommand_core.dispatch(self.core, *parts)
        d.addCallbacks(_format_result, _format_error)
        return d

    def do_BONAFIDE(self, *parts):
        bonafide = self._get_service('bonafide')
        bonafide.local_tokens = self.core.tokens

        d = self.subcommand_bonafide.dispatch(bonafide, *parts)
        d.addCallbacks(_format_result, _format_error)
        return d

    def do_VPN(self, *parts):
        vpn = self._get_service(self.subcommand_vpn.label)
        subcmd = parts[1]
        if subcmd != 'enable' and not vpn:
            return _format_result({'vpn': 'disabled'})

        dispatch = self.subcommand_vpn.dispatch
        if subcmd in ('enable', 'disable'):
            d = dispatch(self.core, *parts)
        else:
            d = dispatch(vpn, *parts)

        d.addCallbacks(_format_result, _format_error)
        return d

    def do_MAIL(self, *parts):
        subcmd = parts[1]
        dispatch = self.subcommand_mail.dispatch

        if subcmd == 'enable':
            d = dispatch(self.core, *parts)

        mail = self._get_service(self.subcommand_mail.label)
        bonafide = self._get_service('bonafide')
        kw = {'bonafide': bonafide}

        if not mail:
            return _format_result({'mail': 'disabled'})

        if subcmd == 'disable':
            d = dispatch(self.core, *parts)
        elif subcmd != 'enable':
            d = dispatch(mail, *parts, **kw)

        d.addCallbacks(_format_result, _format_error)
        return d

    def do_WEBUI(self, *parts):
        subcmd = parts[1] if parts and len(parts) > 1 else None
        dispatch = self.subcommand_webui.dispatch

        if subcmd == 'enable':
            d = dispatch(self.core, *parts)

        webui_label = 'web'
        webui = self._get_service(webui_label)
        kw = {}

        if not webui:
            return _format_result({'webui': 'disabled'})
        if subcmd == 'disable':
            d = dispatch(self.core, *parts)
        elif subcmd != 'enable':
            d = dispatch(webui, *parts, **kw)

        d.addCallbacks(_format_result, _format_error)
        return d

    def do_KEYS(self, *parts):
        dispatch = self.subcommand_keys.dispatch

        keymanager_label = 'keymanager'
        keymanager = self._get_service(keymanager_label)
        bonafide = self._get_service('bonafide')
        kw = {'bonafide': bonafide}

        if not keymanager:
            return _format_result('keymanager: disabled')

        d = dispatch(keymanager, *parts, **kw)
        d.addCallbacks(_format_result, _format_error)
        return d

    def do_EVENTS(self, *parts):
        dispatch = self.subcommand_events.dispatch
        d = dispatch(None, *parts)
        d.addCallbacks(_format_result, _format_error)
        return d

    def dispatch(self, msg):
        cmd = msg[0]
        _method = getattr(self, 'do_' + cmd.upper(), None)

        if not _method:
            return defer.fail(failure.Failure(RuntimeError('No such command')))

        return defer.maybeDeferred(_method, *msg)

    def _get_service(self, name):
        try:
            return self.core.getServiceNamed(name)
        except KeyError:
            return None


def _format_result(result):
    if isinstance(result, dict) and result.get('error'):
        error = result['error']
    else:
        error = None
    return json.dumps({'error': error, 'result': result})


def _format_error(failure):
    """
    Logs the failure backtrace, and returns a json containing the error
    message.

    If a exception declares the 'expected' attribute as True,
    we will not print a full traceback. instead, we will dispatch
    the ``exception`` message attribute as the ``error`` field in the response
    json.
    """

    expected = getattr(failure.value, 'expected', False)
    if not expected:
        log.error('[DISPATCHER] Unexpected error!')
        log.error('{0!r}'.format(failure.value))
        log.error(failure.getTraceback())

    # if needed, we could add here the exception type as an extra field
    return json.dumps({'error': failure.value.message, 'result': None})
