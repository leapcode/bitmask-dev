# -*- coding: utf-8 -*-
# _http.py
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

"""
twisted.web utils for bonafide.
"""

import cookielib
import os
import urllib

from leap.common.files import get_mtime

from twisted.logger import Logger
from twisted.internet import defer, protocol, reactor
from twisted.internet.ssl import Certificate
from twisted.python.filepath import FilePath
from twisted.web.client import Agent, CookieAgent
from twisted.web.client import BrowserLikePolicyForHTTPS
from twisted.web.http_headers import Headers
from twisted.web.iweb import IBodyProducer
from zope.interface import implements


log = Logger()


def cookieAgentFactory(verify_path, connectTimeout=30):
    customPolicy = BrowserLikePolicyForHTTPS(
        Certificate.loadPEM(FilePath(verify_path).getContent()))
    agent = Agent(reactor, customPolicy, connectTimeout=connectTimeout)
    cookiejar = cookielib.CookieJar()
    return CookieAgent(agent, cookiejar)


class Unchanged(Exception):
    pass


# TODO this should be ported to use treq client.

def httpRequest(agent, url, values=None, headers=None,
                method='POST', token=None, saveto=None):
    if values is None:
        values = {}
    if headers is None:
        headers = {}

    data = ''
    mtime = None
    if values:
        data = urllib.urlencode(values)
        headers['Content-Type'] = ['application/x-www-form-urlencoded']

    isfile = os.path.isfile

    if saveto is not None and isfile(saveto):
        # TODO - I think we need a force parameter, because we might have a
        # malformed file. Or maybe just remove the file if sanity check does
        # not pass.
        mtime = get_mtime(saveto)
        if mtime is not None:
            headers['if-modified-since'] = [mtime]

    if token:
        headers['Authorization'] = ['Token token="%s"' % (bytes(token))]

    def handle_response(response):
        log.debug("RESPONSE %s %s %s" % (method, response.code, url))
        if response.code == 204:
            d = defer.succeed('')
        if saveto and mtime and response.code == 304:
            log.debug('304 (Not modified): %s' % url)
            raise Unchanged()
        else:
            class SimpleReceiver(protocol.Protocol):
                def __init__(s, d):
                    s.buf = ''
                    s.d = d

                def dataReceived(s, data):
                    s.buf += data

                def connectionLost(s, reason):
                    # TODO: test if reason is twisted.web.client.ResponseDone,
                    # if not, do an errback
                    s.d.callback(s.buf)
            d = defer.Deferred()
            response.deliverBody(SimpleReceiver(d))
        return d

    def passthru(failure):
        failure.trap(Unchanged)

    d = agent.request(method, url, Headers(headers),
                      StringProducer(data) if data else None)
    d.addCallback(handle_response)
    if saveto:
        d.addCallback(lambda body: _write_to_file(body, saveto))
        d.addErrback(passthru)
    return d


def _write_to_file(content, path):
    folder = os.path.split(path)[0]
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with open(path, 'w') as f:
        f.write(content)
    # touch it to update its utime
    os.utime(path, None)


class StringProducer(object):

    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass
