# -*- coding: utf-8 -*-
# systray.py
# Copyright (C) 2017 LEAP Encryption Acess Project
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
PyQt5 Systray Integration
"""

from leap.common.events import client as leap_events
from leap.common.events import catalog

from leap.bitmask.gui import app_rc

import platform

if platform.system() == 'Windows':
    from PySide.QtGui import QDialog
else:
    from PyQt5.QtGui import QIcon
    from PyQt5.QtGui import QPixmap
    from PyQt5.QtWidgets import QDialog
    from PyQt5.QtWidgets import QAction
    from PyQt5.QtWidgets import QMenu
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtWidgets import QSystemTrayIcon
    from PyQt5.QtWidgets import QWidget


# TODO do switch based on theme
# TODO get also blocked icon
# TODO get spinning motion


if platform.system() == 'Darwin':
    TRAY_ICONS = (':/white/64/wait.png',
                  ':/white/64/on.png',
                  ':/white/64/off.png',
                  ':/white/64/blocked.png')
else:
    TRAY_ICONS = (':/black/64/wait.png',
                  ':/black/64/on.png',
                  ':/black/64/off.png',
                  ':/black/64/blocked.png')


# TODO I think this does not need QDialog

class WithTrayIcon(QWidget):

    user_closed = False

    def setupSysTray(self):
        self._createIcons()
        self._createActions()
        self._createTrayIcon()
        self.trayIcon.activated.connect(self.iconActivated)
        self.setVPNStatus('off')
        self.setUpEventListener()
        self.trayIcon.show()

    def setVPNStatus(self, status):
        seticon = self.trayIcon.setIcon
        settip = self.trayIcon.setToolTip
        # XXX this is an oversimplification, see #9131
        # the simple state for failure is off too, for now.
        if status == 'off':
            seticon(self.ICON_OFF)
            settip('VPN: Off')
        elif status == 'on':
            seticon(self.ICON_ON)
            settip('VPN: On')
        elif status == 'starting':
            seticon(self.ICON_WAIT)
            settip('VPN: Starting')
        elif status == 'stopping':
            seticon(self.ICON_WAIT)
            settip('VPN: Stopping')

    def setUpEventListener(self):
        leap_events.register(
            catalog.VPN_STATUS_CHANGED,
            self._handle_vpn_event)

    def _handle_vpn_event(self, *args):
        status = None
        if len(args) > 1:
            status = args[1]
            self.setVPNStatus(status.lower())

    def _createIcons(self):
        self.ICON_WAIT = QIcon(QPixmap(TRAY_ICONS[0]))
        self.ICON_ON = QIcon(QPixmap(TRAY_ICONS[1]))
        self.ICON_OFF = QIcon(QPixmap(TRAY_ICONS[2]))
        self.ICON_BLOCKED = QIcon(QPixmap(TRAY_ICONS[3]))

    def _createActions(self):
        self.quitAction = QAction(
            "&Quit", self,
            triggered=self.closeFromSystray)

    def iconActivated(self, reason):
        # can use .Trigger also for single click
        if reason in (QSystemTrayIcon.DoubleClick, ):
            self.showNormal()

    def closeFromSystray(self):
        self.user_closed = True
        self.close()

    def _createTrayIcon(self):
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

    def closeEvent(self, event):
        if self.trayIcon.isVisible() and not self.user_closed:
            QMessageBox.information(
                self, "Bitmask",
                "Bitmask will minimize to the system tray. "
                "You can choose 'Quit' from the menu with a "
                "right click on the icon, and restore the window "
                "with a double click.")
        self.hide()
        if not self.user_closed:
            event.ignore()
