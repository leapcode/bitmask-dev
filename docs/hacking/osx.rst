.. _osx-dev:

Setting up a development environment in OSX™
============================================

.. note: work in progress. send a MR if you spot any mistake or missing info!

* You will need to install xcode and the command line developer tools (``xcode-select --install``).

* Use ``brew`` to install ``OpenSSL``: ``brew install openssl``

* Install ``wget``: ``brew install wget`` (interestingly, this installs openssl 1.1, which we might want in order not to use the python scrypt extension).

* Install a recent python: ``brew install python``

* Put the installed python in your path: ``echo 'export PATH="/usr/local/opt/python/libexec/bin:$PATH"' >> ~/.bash_profile``

* Log-in again so that the $PATH changes take effect.

* Make sure you're using a new enough version of pip (1.8 or newest). This will make all the problems with ``cryptography`` going away, since it will install the statically built wheel: ``pip --version``

Clone the repo, create and activate a virtualenv::

  mkdir ~/leap && cd ~/leap
  git clone "https://0xacab.org/leap/bitmask-dev"
  pip install virtualenv
  virtualenv ~/leap/venv
  source ~/leap/venv/bin/activate

In OSX, we're using ``pywebview`` for the GUI launcher, that depends on ``pyobjc``. You can install that with::

  pip install -r ~/leap/bitmask-dev/pkg/requirements-osx.pip

* Install the rest of dependencies as usual.

You also want to build the thirdparty binaryes (openvpn, gpg)::

  cd pkg/thirdparty/gnupg && ./build_gnupg.sh


After installing that, you should be able to build the bundle::

  make bundle_osx


Privileged helper
=================

The OSX privileged helper is in ``src/leap/bitmask/vpn/helpers/osx/``.

It is a python daemon that runs as root.
It should be installed by the Bitmask installer.

If you have to stop it::

  sudo launchctl unload /Library/LaunchDaemons/se.leap.bitmask-helper.plist


And, to load it again::

  sudo launchctl load /Library/LaunchDaemons/se.leap.bitmask-helper.plist

For convenience while developing, you can find a Makefile to install and load
the helpers in ``pkg/tools/osx``. Be aware that, for the time being, Bitmask
and RiseupVPN share the same bitmask-helper, so you should have installed only
one of them at the same time.


Debugging bitmask-helper
------------------------

Bitmask communicates with the privileged ``bitmask-helper`` through a unix
socket. If you need to debug the privileged helper (for instance, if you need to
tear down the firewall after a crash), you can do it like this with
``socat``::

  echo 'firewall_stop/CMD' | socat - UNIX-CONNECT:/var/run/bitmask-helper.socket


Other helpers
-------------

There are other helpers that the installer drops in a well-know path.
These are shipped in ``pkg/osx``, and copied to
``/Applications/Bitmask.app/Contents/Resources``.


OSX Firewall
------------

The OSX Firewall lives in ``src/leap/bitmask/vpn/helpers/osx/bitmask.pf.conf``. It gets
installed to the same path mentioned in the previous section.

.. note: cleanup unused helpers

Uninstalling
===================================

There's an uninstall script in `pkg/osx/uninstall.sh`.

Installing the bundle with homebrew
===================================

For testing purposes, `homebrew`_ can be used to distribute and install
experimental versions of the bundle. This should download and install the
latest version of the bundle::

  brew install kalikaneko/bitmask/bitmask

After that, you should be able to launch the bundle::

  bitmask


.. _`homebrew`: https://brew.sh/


Debug logs
----------

Bitmask rotates logs. The latest one can be found at::

  /Users/<youruser>/Library/Preferences/leap/bitmaskd.log


Known Issues
------------

The current state of the bundle that is distributed with homebrew is yet buggy,
so it's in a pre-alpha state. Reports or bugfixes are welcome a this point.

Major blockers for a usable homebrew distribution are:

* Cannot find the gpg binary installed by homebrew https://0xacab.org/leap/bitmask-dev/issues/8934

How to produce a bundle to be distributed via homebrew
------------------------------------------------------

(This section is maintainer notes, but it can be useful also for you if you are working
on changes that affect distribution and you want let others test your work.)

The original homebrew formula is in ``https://github.com/kalikaneko/homebrew-bitmask/blob/master/bitmask.rb``.

When running ``make bundle_osx``, PyInstaller generates two different folders
(the initial PyInstaller folders get some extra files added by the rules in
the makefile). One is the OSX Bundle - that is distributed by the installer in
the form of a `.pkg` , and the other is the bare libs folder. The Bitmask
Formula instructs homebrew to fetch a tar.gz with this last folder, so first
step is preparing the tarball::

  cd dist && tar cvzf bitmask-`cat ../pkg/next-version`.tar.gz bitmask-`cat pkg/next-version`

If you already uploaded a bundle with that version, make sure that you rename it
to include a patch version before uploading it::

  scp dist/bitmask-`cat pkg/next-version` downloads.leap.se:./client/osx/internal/

Then the ``version`` file needs to be changed in the Formula.  The ``sha256``
field has also to be updated, you can get the value with::

   shasum -a 256 bitmask-0.10a1p2.tar.gz


OSX Development Roadmap
=======================

1. [done] Get a smooth 0.10 installation experience for power-users via homebrew.
2. [done] Merge bugfixes.
3. Distribute Bitmask.pkg again, with the installer executing the same
   installation scripts as homebrew Formula is doing.


Other notes
===========

PySide vs QtWebKit
------------------

http://qtwebkit.blogspot.nl/2016/08/qtwebkit-im-back.html

Running OSX on KVM
------------------

The following notes are not yet tested, but might be useful for development.

* https://github.com/kholia/OSX-KVM

