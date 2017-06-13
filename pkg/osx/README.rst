Helper files needed for OSX
===========================

* The bitmask-helper that is run as root can be found in the source tree, in
``src/leap/bitmask/vpn/helpers/osx``.
* python ``daemon`` is a dependency for the bitmask-helper, here it is vendored.
* The plist file ``se.leap.bitmask-helper.plist`` (this should be installed into
  /Library/LaunchDaemons/se.leap.bitmask-helper.plist).
* OpenVPN up/down scripts: ``openvpn/client.down.sh`` and
  ``openvpn/client.up.sh``.



