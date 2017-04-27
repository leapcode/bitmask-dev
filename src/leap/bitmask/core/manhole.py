# -*- coding: utf-8 -*-
# manhole.py
# Copyright (C) 2014-2017 LEAP
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
Utilities for enabling the manhole administrative interface into Bitmask Core.
"""

PORT = 2222


def getManholeFactory(namespace, user, secret, keydir=None):
    """
    Get an administrative manhole into the application.

    :param namespace: the namespace to show in the manhole
    :type namespace: dict
    :param user: the user to authenticate into the administrative shell.
    :type user: str
    :param secret: pass for this manhole
    :type secret: str
    """
    import string

    from twisted.cred import portal
    from twisted.conch import manhole, manhole_ssh
    from twisted.conch import recvline
    from twisted.conch.insults import insults
    from twisted.conch.ssh import keys
    from twisted.cred.checkers import (
        InMemoryUsernamePasswordDatabaseDontUse as MemoryDB)
    from twisted.python import filepath

    try:
        from IPython.core.completer import Completer
    except ImportError:
        from rlcompleter import Completer

    class EnhancedColoredManhole(manhole.ColoredManhole):
        """
        A nicer Manhole with some autocomplete support.

        See the patch in https://twistedmatrix.com/trac/ticket/6863
        Since you're reading this, it'd be good if *you* can help getting that
        patch into twisted :)
        """

        completion = True

        def handle_TAB(self):
            """
            If tab completion is available and enabled then perform some tab
            completion.
            """
            if not self.completion:
                recvline.HistoricRecvLine.handle_TAB(self)
                return
            # If we only have whitespace characters on this line we pass
            # through the tab
            if set(self.lineBuffer).issubset(string.whitespace):
                recvline.HistoricRecvLine.handle_TAB(self)
                return
            cp = Completer(namespace=self.namespace)
            cp.limit_to__all__ = False
            lineLeft, lineRight = self.currentLineBuffer()

            # Extract all the matches
            matches = []
            n = 0
            while True:
                match = cp.complete(lineLeft, n)
                if match is None:
                    break
                n += 1
                matches.append(match)

            if not matches:
                return

            if len(matches) == 1:
                # Found the match so replace the line. This is apparently how
                # we replace a line
                self.handle_HOME()
                self.terminal.eraseToLineEnd()

                self.lineBuffer = []
                self._deliverBuffer(matches[0] + lineRight)
            else:
                # Must have more than one match, display them
                matches.sort()
                self.terminal.write("\n")
                self.terminal.write("   ".join(matches))
                self.terminal.write("\n\n")
                self.drawInputLine()

        def keystrokeReceived(self, keyID, modifier):
            """
            Act upon any keystroke received.
            """
            self.keyHandlers.update({'\b': self.handle_BACKSPACE})
            m = self.keyHandlers.get(keyID)
            if m is not None:
                m()
            elif keyID in string.printable:
                self.characterReceived(keyID, False)

    class chainedProtocolFactory:
        def __init__(self, namespace):
            self.namespace = namespace

        def __call__(self):
            return insults.ServerProtocol(
                EnhancedColoredManhole, self.namespace)

    sshRealm = manhole_ssh.TerminalRealm()
    sshRealm.chainedProtocolFactory = chainedProtocolFactory(namespace)

    checker = MemoryDB(**{user: secret})
    sshPortal = portal.Portal(sshRealm, [checker])
    sshFactory = manhole_ssh.ConchFactory(sshPortal)

    if not keydir:
        from twisted.python._appdirs import getDataDirectory
        keydir = getDataDirectory()

    keyLocation = filepath.FilePath(keydir).child('id_rsa')
    sshKey = keys._getPersistentRSAKey(keyLocation, 4096)
    sshFactory.publicKeys[b"ssh-rsa"] = sshKey
    sshFactory.privateKeys[b"ssh-rsa"] = sshKey
    return sshFactory
