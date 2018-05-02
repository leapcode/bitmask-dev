# -*- coding: utf-8 -*-
# app.py
# Copyright (C) 2016-2017 LEAP Encryption Acess Project
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
Main entrypoint for the Bitmask Qt GUI.
It just launches a wekbit browser that runs the local web-ui served by bitmaskd
when the web service is running.
"""

import ctypes
import os
import platform
import signal
import sys
import webbrowser

from ctypes import util
from functools import partial
from multiprocessing import Process

from leap.bitmask.system import IS_WIN
from leap.bitmask.core.launcher import run_bitmaskd, pid
from leap.bitmask.gui.systray import WithTrayIcon
from leap.bitmask.gui.housekeeping import cleanup, terminate, reset_authtoken
from leap.bitmask.gui.housekeeping import get_authenticated_url
from leap.bitmask.gui.housekeeping import NoAuthTokenError
from leap.bitmask.gui.housekeeping import check_stale_pidfile


HAS_WEBENGINE = False


# This is a workaround for #9278.
# See https://bugs.launchpad.net/ubuntu/+source/
# qtbase-opensource-src/+bug/1761708
ctypes.CDLL(util.find_library('GL'), ctypes.RTLD_GLOBAL)

if platform.system() == 'Windows':
    from multiprocessing import freeze_support
    from PySide import QtCore, QtGui
    from PySide.QtGui import QDialog
    from PySide.QtGui import QApplication
    from PySide.QtWebKit import QWebView, QGraphicsWebView
else:
    from PyQt5 import QtCore, QtGui
    from PyQt5.QtCore import QObject, pyqtSlot
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QIcon
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtWidgets import QAction
    from PyQt5.QtWidgets import QMenu
    from PyQt5.QtWidgets import QDialog
    from PyQt5.QtWidgets import QMessageBox

    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView
        from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings
        from PyQt5.QtWebChannel import QWebChannel
        HAS_WEBENGINE = True
    except ImportError:
        from PyQt5.QtWebKitWidgets import QWebView
        from PyQt5.QtWebKit import QWebSettings


DEBUG = os.environ.get("DEBUG", False)

BITMASK_URI = 'http://localhost:7070/'
PIXELATED_URI = 'http://localhost:9090/'

qApp = None
bitmaskd = None
browser = None


class BrowserWindow(QWebView, WithTrayIcon):
    """
    This qt-webkit window exposes a couple of callable objects through the
    python-js bridge:

        bitmaskApp.shutdown() -> shut downs the backend and frontend.
        bitmaskApp.openSystemBrowser(url) -> opens URL in system browser
        bitmaskBrowser.openPixelated() -> opens Pixelated app in a new window.

    This BrowserWindow assumes that the backend is already running, since it is
    going to look for the authtoken in the configuration folder.
    """

    def __init__(self, *args, **kw):
        url = kw.pop('url', None)
        first = False
        if not url:
            url = get_authenticated_url()
            first = True
        self.url = url
        self.closing = False

        super(QWebView, self).__init__(*args, **kw)
        self.setWindowTitle('Bitmask')
        self.bitmask_browser = NewPageConnector(self) if first else None
        self.loadPage(self.url)

        self.bridge = AppBridge(self) if first else None

        if self.bridge is not None and HAS_WEBENGINE:
            print "[+] registering python<->js bridge"
            channel = QWebChannel(self)
            channel.registerObject("bitmaskApp", self.bridge)
            self.page().setWebChannel(channel)

        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/mask-icon.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

    def loadPage(self, web_page):
        if os.path.isabs(web_page):
            web_page = os.path.relpath(web_page)

        url = QtCore.QUrl(web_page)
        self.load(url)

    def shutdown(self, *args):
        global bitmaskd
        if self.closing:
            return
        self.closing = True

        bitmaskd.join()
        terminate(pid)
        cleanup()
        print('[bitmask] shutting down gui...')

        try:
            self.stop()
            try:
                global pixbrowser
                pixbrowser.stop()
                del pixbrowser
            except:
                pass
            QtCore.QTimer.singleShot(0, qApp.deleteLater)

        except Exception as ex:
            print('exception catched: %r' % ex)
            sys.exit(1)


class AppBridge(QObject):

    @pyqtSlot()
    def shutdown(self):
        print "[+] shutdown called from js"
        global browser
        if browser:
            browser.user_closed = True
            browser.close()

    @pyqtSlot(str)
    def openSystemBrowser(self, url):
        webbrowser.open(url)


pixbrowser = None
closing = False


class NewPageConnector(QObject):

    @pyqtSlot()
    def openPixelated(self):
        global pixbrowser
        pixbrowser = BrowserWindow(url=PIXELATED_URI)
        pixbrowser.show()


def _handle_kill(*args, **kw):
    global pixbrowser
    global closing
    if closing:
        sys.exit()
    win = kw.get('win')
    if win:
        win.user_closed = True
        QtCore.QTimer.singleShot(0, win.close)
    if pixbrowser:
        QtCore.QTimer.singleShot(0, pixbrowser.close)
    closing = True


def launch_backend():
    global bitmaskd
    check_stale_pidfile()
    bitmaskd = Process(target=run_bitmaskd,
                       kwargs={'app_name': 'Bitmask',
                               'exec_path': sys.argv[0]})
    bitmaskd.start()


def launch_gui(with_window=True):
    global qApp
    global browser

    if IS_WIN:
        freeze_support()

    launch_backend()
    qApp = QApplication([])
    try:
        browser = BrowserWindow(None)
    except NoAuthTokenError as e:
        print('ERROR: ' + e.message)
        sys.exit(1)

    browser.setupSysTray()

    qApp.setQuitOnLastWindowClosed(True)
    qApp.lastWindowClosed.connect(browser.shutdown)

    signal.signal(
        signal.SIGINT,
        partial(_handle_kill, win=browser))

    # Avoid code to get stuck inside c++ loop, returning control
    # to python land.
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(500)

    if with_window:
        browser.show()

    sys.exit(qApp.exec_())


usage = '''bitmask [<args>]

Launches the Bitmask GUI.

OPTIONAL ARGUMENTS:

  --nowindow   does not launch the main window, only the systray.

SEE ALSO:

  bitmaskctl   controls bitmask daemon from the command line.
'''


def start_app():
    from leap.bitmask.util import STANDALONE
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

    # Allow the frozen binary in the bundle double as the cli entrypoint
    # Why have only a user interface when you can have two?

    if DEBUG:
        os.environ.setdefault('QTWEBENGINE_REMOTE_DEBUGGING', '8081')

    if platform.system() == 'Windows':
        # In windows, there are some args added to the invocation
        # by PyInstaller, I guess...
        MIN_ARGS = 3
    else:
        MIN_ARGS = 1

    # DEBUG ====================================
    if len(sys.argv) > MIN_ARGS:
        if STANDALONE:
            if sys.argv[1] == 'bitmask_helpers':
                from leap.bitmask.vpn.helpers import main
                return main()

            from leap.bitmask.cli import bitmask_cli
            return bitmask_cli.main()
        else:
            if sys.argv[1] == '--help' or sys.argv[1] == 'help':
                print(usage)
                sys.exit()

    reset_authtoken()
    with_window = '--nowindow' not in sys.argv
    launch_gui(with_window)


if __name__ == "__main__":
    start_app()
