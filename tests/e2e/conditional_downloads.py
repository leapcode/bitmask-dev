#!/usr/bin/env python
"""
Exercises the bonafide http module against a real server.
Checks for the conditional header behavior, ensuring that we do not write a
config file if we receive a 304 Not Modified response.
"""
import uuid
import os
import tempfile
import shutil

from twisted.internet import defer
from twisted.internet.task import react

from leap.bitmask.bonafide._http import httpRequest
from leap.common import http

URI = 'https://demo.bitmask.net/1/configs/eip-service.json'
tmp = tempfile.mkdtemp()


@defer.inlineCallbacks
def main(reactor, *args):
    client = http.HTTPClient()
    fname = os.path.join(tmp, str(uuid.uuid4()))
    yield httpRequest(client._agent, URI, method='GET', saveto=fname)
    filesize = os.path.getsize(fname)
    assert filesize > 1
    # touch file to 5 minutes in the past
    past = int(os.path.getmtime(fname)) - 300
    os.utime(fname, (past, past))
    assert os.path.getmtime(fname) == past
    yield httpRequest(client._agent, URI, method='GET', saveto=fname)
    # it was not modified
    assert os.path.getmtime(fname) == past
    print 'OK'
    shutil.rmtree(tmp)


react(main, [])
