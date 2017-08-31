# -*- coding: utf-8 -*-
# service.py
# Copyright (C) 2015 LEAP
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
Bitmask-core Service.
"""
import os
import uuid
try:
    import resource
except ImportError:
    pass

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.logger import Logger

from leap.bitmask import __version__
from leap.bitmask.core import configurable
from leap.bitmask.core import manhole
from leap.bitmask.core import flags
from leap.bitmask.core import _zmq
from leap.bitmask.core import _session
from leap.bitmask.core.web.service import HTTPDispatcherService
from leap.common.events import server as event_server
try:
    from leap.bitmask.vpn.service import VPNService
    HAS_VPN = True
except ImportError as exc:
    HAS_VPN = False


backend = flags.BACKEND

if backend == 'default':
    from leap.bitmask.core import mail_services
    from leap.bitmask.bonafide.service import BonafideService
elif backend == 'dummy':
    from leap.bitmask.core.dummy import mail_services
    from leap.bitmask.core.dummy import BonafideService
else:
    raise RuntimeError('Backend not supported')


log = Logger()


class BitmaskBackend(configurable.ConfigurableService):

    """
    The Bitmask Core Backend Service.
    Here is where the multiple service tree gets composed.
    This is passed to the command dispatcher.
    """

    def __init__(self, basedir=configurable.DEFAULT_BASEDIR):

        configurable.ConfigurableService.__init__(self, basedir)
        self.core_commands = BackendCommands(self)

        # The global token is used for authenticating some of the channels that
        # expose the dispatcher. For the moment being, this is the REST API.
        self.global_tokens = [uuid.uuid4().hex]
        log.debug(
            'Global token: {0}'.format(self.global_tokens[0]))
        self._touch_token_file()

        # These tokens are user-session tokens. Implemented and rolled back,
        # unused for now. If we don't move forward with user-session tokens on
        # top of the global app token, this should be removed.
        self.tokens = {}

        def with_manhole():
            user = self.get_config('manhole', 'user', '')
            passwd = self.get_config('manhole', 'passwd', '')
            port = self.get_config('manhole', 'port', manhole.PORT)
            if user and passwd:
                conf = {'user': user, 'passwd': passwd, 'port': port}
                return conf
            return None

        on_start = reactor.callWhenRunning

        on_start(self.init_events)
        on_start(self.init_bonafide)
        on_start(self.init_sessions)

        if self._enabled('mail'):
            on_start(self._init_mail_services)

        if self._enabled('vpn'):
            on_start(self._init_vpn)

        if self._enabled('zmq'):
            on_start(self._init_zmq)

        if self._enabled('web'):
            onion = self._enabled('onion')
            on_start(self._init_web, onion=onion)

        if self._enabled('websockets'):
            on_start(self._init_websockets)

        manholecfg = with_manhole()
        if manholecfg:
            on_start(self._init_manhole, manholecfg)

    def _enabled(self, service):
        return self.get_config('services', service, False, boolean=True)

    def _touch_token_file(self):
        path = os.path.join(self.basedir, 'authtoken')
        with open(path, 'w') as f:
            f.write(self.global_tokens[0])
        os.chmod(path, 0600)

    def init_events(self):
        event_server.ensure_server()

    def init_bonafide(self):
        bf = BonafideService(self.basedir)
        bf.setName('bonafide')
        bf.setServiceParent(self)
        # TODO ---- these hooks should be activated only if
        # (1) we have enabled that service
        # (2) provider offers this service
        bf.register_hook('on_passphrase_entry', listener='soledad')
        bf.register_hook('on_bonafide_auth', listener='soledad')
        bf.register_hook('on_passphrase_change', listener='soledad')
        bf.register_hook('on_bonafide_auth', listener='keymanager')
        bf.register_hook('on_bonafide_auth', listener='mail')
        bf.register_hook('on_bonafide_logout', listener='mail')

    def init_sessions(self):
        sessions = _session.SessionService(self.basedir, self.tokens)
        sessions.setServiceParent(self)

    def _start_child_service(self, name):
        service = self.getServiceNamed(name)
        if service and not service.running:
            log.debug('Starting backend child service: %s' % name)
            service.startService()

    def _stop_child_service(self, name):
        log.debug('Stopping backend child service: %s' % name)
        service = self.getServiceNamed(name)
        if service:
            service.stopService()

    def _init_mail_services(self):
            self._init_soledad()
            self._init_keymanager()
            self._init_mail()

    def _start_mail_services(self):
        self._start_child_service('soledad')
        self._start_child_service('keymanager')
        self._start_child_service('mail')

    def _stop_mail_services(self):
        self._stop_child_service('mail')
        self._stop_child_service('keymanager')
        self._stop_child_service('soledad')

    def _init_soledad(self):
        service = mail_services.SoledadService
        sol = self._maybe_init_service(
            'soledad', service, self.basedir)
        if sol:
            sol.register_hook(
                'on_new_soledad_instance', listener='keymanager')
            sol.register_hook(
                'on_soledad_first_sync', listener='keymanager')

            # XXX this might not be the right place for hooking the sessions.
            # If we want to be offline, we need to authenticate them after
            # soledad. But this is not valid for the VPN case,
            # because we have not decided if soledad is required in that case
            # (seemingly not). If only VPN, then we have to return the token
            # from the SRP authentication.
            sol.register_hook(
                'on_new_soledad_instance', listener='sessions')

    def _init_keymanager(self):
        service = mail_services.KeymanagerService
        km = self._maybe_init_service(
            'keymanager', service, self.basedir)
        if km:
            km.register_hook('on_new_keymanager_instance', listener='mail')

    def _init_mail(self):
        service = mail_services.StandardMailService
        self._maybe_init_service('mail', service, self.basedir,
                                 self._enabled('mixnet'))

    def _init_vpn(self):
        if HAS_VPN:
            cfg = self.get_config_section('vpn')
            self._maybe_init_service('vpn', VPNService, cfg)

    def _init_zmq(self):
        zs = _zmq.ZMQServerService(self)
        zs.setServiceParent(self)

    def _init_web(self, onion=False):
        service = HTTPDispatcherService
        self._maybe_init_service('web', service, self, onion=onion)

    def _init_websockets(self):
        from leap.bitmask.core import websocket
        ws = websocket.WebSocketsDispatcherService(self)
        ws.setServiceParent(self)

    def _maybe_init_service(self, label, klass, *args, **kw):
        try:
            service = self.getServiceNamed(label)
        except KeyError:
            service = klass(*args, **kw)
            service.setName(label)
            service.setServiceParent(self)
        return service

    def _init_manhole(self, cfg):
        port = cfg['port']
        user, passwd = cfg['user'], cfg['passwd']
        sshFactory = manhole.getManholeFactory(
            {'core': self}, user, passwd)
        endpoint = TCP4ServerEndpoint(reactor, port)
        endpoint.listen(sshFactory)

        log.info('Started manhole in PORT {0!s}'.format(port))

    def do_stats(self):
        return self.core_commands.do_stats()

    def do_status(self):
        return self.core_commands.do_status()

    def do_version(self):
        return self.core_commands.do_version()

    def do_stop(self):
        for service in self:
            try:
                service.stopService()
            except Exception as e:
                log.error('Error stopping service... {0!r}'.format(e))
        return self.core_commands.do_stop()

    # Service Toggling

    def do_enable_service(self, service):
        assert service in self.service_names
        self.set_config('services', service, 'True')

        if service == 'mail':
            self._init_mail_services()
            self._start_mail_services()

        elif service == 'vpn':
            self._init_vpn()

        elif service == 'zmq':
            self._init_zmq()

        elif service == 'web':
            self._init_web()

        return {'enabled': 'ok'}

    def do_disable_service(self, service):
        assert service in self.service_names

        if service == 'mail':
            self._stop_mail_services()

        self.set_config('services', service, 'False')
        return {'disabled': 'ok'}


class BackendCommands(object):

    """
    General Commands for the BitmaskBackend Core Service.
    """

    def __init__(self, core):
        self.core = core

    def do_status(self):
        # we may want to make this tuple a class member
        services = ('soledad', 'keymanager', 'mail', 'vpn', 'web')

        status = {}
        for name in services:
            _status = 'stopped'
            try:
                if self.core.getServiceNamed(name).running:
                    _status = 'running'
            except KeyError:
                pass
            status[name] = _status
        status['backend'] = flags.BACKEND

        return status

    def do_version(self):
        return {'version_core': __version__}

    def do_stats(self):
        mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return {'mem_usage': '%s MB' % (mem / 1024)}

    def do_stop(self):
        self.core.stopService()
        reactor.callLater(1, reactor.stop)
        return {'stop': 'ok'}
