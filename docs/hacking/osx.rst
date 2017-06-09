.. _osx-dev:

Setting up a development environment in OSX™
============================================

.. note: work in progress

* Make sure you're using a new enough version of pip (1.8 or newest).
This will make all the problems with ``cryptography`` going away, since it will
install the statically built wheel.

* Use ``brew`` to install ``OpenSSL``.

* **Problem**: pyqt5 in homebrew stopped shipping qtwebkit. I found the following
workaround in an issue in qutebrowser's repo, works fine for me for now::

  cd $(brew --prefix)/Library/Formula
  curl -OO
  https://raw.githubusercontent.com/Homebrew/homebrew/f802822b0fa35ad362aebd0101ccf83a638bed37/Library/Formula/{py,}qt5.rb
  brew install qt5 pyqt5

Privileged helper
=================

The OSX privileged helper is in ``src/leap/bitmask/vpn/fw/osx/``.

.. note: move it to vpn/helpers/osx

It is a python daemon that runs as root.
It should be installed by the Bitmask installer.

If you have to stop it::

  sudo launchctl unload /Library/LaunchDaemons/se.leap.bitmask-helper.plist


And, to load it again::

  sudo launchctl load /Library/LaunchDaemons/se.leap.bitmask-helper.plist


Debugging bitmask-helper
------------------------

Bitmask communicates with the privileged ``bitmask-helper`` through a unix
socket. If you need to debug the privileged helper (for instance, if you need to
tear down the firewall after a crash), you can do it like this with
``socat``::

  echo 'firewall_stop/CMD' | socat - UNIX-CONNECT:/tmp/bitmask-helper.socket


Other helpers
-------------

There are other helpers that the installer drops in a well-know path.
These are shipped in ``pkg/osx``, and copied to
``/Applications/Bitmask.app/Contents/Resources``.

.. note: cleanup unused helpers


Other notes
===========

PySide vs QtWebKit
------------------

http://qtwebkit.blogspot.nl/2016/08/qtwebkit-im-back.html

Running OSX on KVM
------------------

The following notes are not yet tested, but might be useful for development.

* https://github.com/kholia/OSX-KVM

