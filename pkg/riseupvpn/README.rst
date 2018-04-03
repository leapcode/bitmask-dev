RiseupVPN
=========

RiseupVPN is a VPN app that is pre-configured for connecting to the anonymous
VPN service offered by Riseup.

Technically, RiseuVPN is a customised build of Bitmask, branded after one of
the major LEAP providers in the wild.

It ships only the set of vpn dependencies for the bitmask daemon, plus a
minimalistic systray written in golang https://0xacab.org/leap/bitmask-systray
that makes use of libappindicator for displaying notifications.

Currently, RiseupVPN is distributed as a snap package. It uses classic
confinement because it needs to install a polkit policy file so that
bitmask-root and openvpn can be executed without asking user for permission
each time.

Usage
-----

You can get the snap from the store::

 sudo apt install snapd
 sudo snap install riseup-vpn --classic

If you want to build the local snap::

 make build
 sudo snap install riseup-vpn_*.snap --classic

That should have added a new application called RiseupVPN in your desktop
launchers. You can also launch it manually like this::

 /snap/bin/riseup-vpn.launcher


