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
confinement because it needs to install bitmask-root in the system, and a
polkit policy file so that bitmask-root and openvpn can be executed without
asking user for permission each time.

Usage
-----

Until the snap package gets approved in the snap store, you can use the snap as follows::

 wget https://downloads.leap.se/RiseupVPN/linux/riseup-vpn_0.10.4_amd64.snap
 sudo apt install snapd
 sudo snap install riseup-vpn_0.10.4_amd64.snap --dangerous --classic

That should have made a new application called RiseupVPN in your launchers.
You can also launch it manually like this::

 /snap/bin/riseup-vpn.launcher


