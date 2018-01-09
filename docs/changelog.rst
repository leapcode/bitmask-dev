Changelog
=====================

0.10.3 -  `master`_ 
-------------------------------
.. note:: This version is not yet released and is under active development.

Features
~~~~~~~~
- `#8217 <https://0xacab.org/leap/bitmask-dev/issues/8217>`_: renew OpenPGP keys before they expire.
- `#9074 <https://0xacab.org/leap/bitmask-dev/issues/9074>`_: pin provider ca certs.
- `#6914 <https://0xacab.org/leap/bitmask-dev/issues/6914>`_: expose an API to retrive message status.
- `#9188 <https://0xacab.org/leap/bitmask-dev/issues/9188>`_: try other gateways if the main one fails.
- `#9125 <https://0xacab.org/leap/bitmask-dev/issues/9125>`_: port to use qtwebengine for rendering UI.
- Set a windows title, so that Bitmask windows can be programmatically manipulated.

Bugfixes
~~~~~~~~
- `#9191 <https://0xacab.org/leap/bitmask-dev/issues/9191>`_: workaround for missing libs needed for qtwebengine.
- `#9171 <https://0xacab.org/leap/bitmask-dev/issues/9171>`_: fix a bug in bootstrap that avoided more than one user to login.
- `#9165 <https://0xacab.org/leap/bitmask-dev/issues/9165>`_: deprecate pyqt5-webkit, use qtwebengine instead.
- `#9137 <https://0xacab.org/leap/bitmask-dev/issues/9137>`_: fix issues with dns resolution with systemd-resolved (mostly ubuntu 17.10).

Misc
~~~~
- Speedup stages on CI.
- Configure travis build for OSX.
- Add tox to the docker image; install it on every job.
- Build openvpn with iproute2 option for bundles.

0.10.2
-------------------------------

Features
~~~~~~~~
- `#9094 <https://0xacab.org/leap/bitmask-dev/issues/9094>`_: Implement a simple systray icon.
- Ship gpg1 binary with osx builds.

Bugfixes
~~~~~~~~
- `#9099 <https://0xacab.org/leap/bitmask-dev/issues/9099>`_: properly check for openvpn binary path in bundles.
- `#9064 <https://0xacab.org/leap/bitmask-dev/issues/9064>`_: keep content-type when it is set in message headers.
- Ship cacert.pem inside Bitmask.app
- Avoid importing linux-specific constants in firewall helpers.

Misc
~~~~
- Build packages for artful too.

0.10.1
---------------------

Bugfixes
~~~~~~~~
- `#9073 <https://0xacab.org/leap/bitmask-dev/issues/9073>`_: fix bootstrapping of providers like riseup.
- Use the right path for firewall in debian packages.

0.10.0 - la rosa de foc
-----------------------

Features
~~~~~~~~
- Initial cli port of the legacy vpn code
- `#8112 <https://0xacab.org/leap/bitmask-dev/issues/8112>`_: Check validity of key signature
- `#8755 <https://0xacab.org/leap/bitmask-dev/issues/8755>`_: Add account based keymanagement API
- `#8770 <https://0xacab.org/leap/bitmask-dev/issues/8770>`_: Simplify mail status in the cli
- `#8769 <https://0xacab.org/leap/bitmask-dev/issues/8769>`_: Eliminate active user from bonafide
- `#8771 <https://0xacab.org/leap/bitmask-dev/issues/8771>`_: Add json print to the cli
- `#8765 <https://0xacab.org/leap/bitmask-dev/issues/8765>`_: Require a global authentication token for the api
- `#8819 <https://0xacab.org/leap/bitmask-dev/issues/8819>`_: Send key to provider if a new priv key is putted in the keyring
- `#8821 <https://0xacab.org/leap/bitmask-dev/issues/8821>`_: Add a 'fetch' flag to key export
- `#8049 <https://0xacab.org/leap/bitmask-dev/issues/8049>`_: Restart the VPN automatically
- `#8852 <https://0xacab.org/leap/bitmask-dev/issues/8852>`_: Stop the vpn (and all services) when application is shut down
- `#8804 <https://0xacab.org/leap/bitmask-dev/issues/8804>`_: Automatic selection of gateways, based on user timezone
- `#8855 <https://0xacab.org/leap/bitmask-dev/issues/8855>`_: Manual override for the vpn gateway selection
- `#8835 <https://0xacab.org/leap/bitmask-dev/issues/8835>`_: On bitmaskclt vpn start use the last vpn if no provider is provided
- `#9059 <https://0xacab.org/leap/bitmask-dev/issues/9059>`_: Automatic renewal of vpn certificate
- `#8895 <https://0xacab.org/leap/bitmask-dev/issues/8895>`_: Check for running pkexec in the system
- `#8977 <https://0xacab.org/leap/bitmask-dev/issues/8977>`_: Download config files if newer ones are found in the provider
- Add VPN API to bitmask.js
- Add vpn get_cert command
- Indicate a successful/failure OpenPGP header import
- Get more detailed status report for email
- VPN and Mail status displayed in the UI
- Port Pixelated UA integration from legacy bitmask
- Add Pixelated Button to the UI
- Add ability to ssh into the bitmask daemon for debug
- Add a call to inject messages into a mailbox using the cli.
- New ``bitmask_chromium`` gui: launches Bitmask UI as a standalone chromium app if chromium is installed in your system
- Add new debianization split, with separated bitmask components.
- `#9029 <https://0xacab.org/leap/bitmask-dev/issues/9029>`_: add a package for the bitmask javascript UI.

Bugfixes
~~~~~~~~
- `#8783 <https://0xacab.org/leap/bitmask-dev/issues/8783>`_: use username instead of provider in the vpn calls
- `#8868 <https://0xacab.org/leap/bitmask-dev/issues/8868>`_: can't upload generated key with bitmask
- `#8832 <https://0xacab.org/leap/bitmask-dev/issues/8832>`_: don't allow putting non-private keys for the keyring address
- `#8901 <https://0xacab.org/leap/bitmask-dev/issues/8901>`_: use gpg1 binary if present
- `#8971 <https://0xacab.org/leap/bitmask-dev/issues/8971>`_: handle 502 replies from nicknym
- `#8957 <https://0xacab.org/leap/bitmask-dev/issues/8957>`_: alot doesn't automatically decrypt messages sent from Bitmask
- Repeat decryption if signed with attached key
-  Log error in case JSON parsing fails for decrypted doc

Misc
~~~~
- Remove usage of soledad offline flag.
- Tests use soledad master instead of develop
- Build bundles with pixelated libraries


0.9.4 - works for you
---------------------

Features
~~~~~~~~
- `#7550 <https://leap.se/code/issues/7550>`_: Add ability to use invite codes during signup
- `#7965 <https://leap.se/code/issues/7965>`_: Add basic keymanagement to the cli.
- `#8265 <https://leap.se/code/issues/8265>`_: Add a REST API and bitmask.js library for it.
- `#8400 <https://leap.se/code/issues/8400>`_: Add manual provider registration.
- `#8435 <https://leap.se/code/issues/8435>`_: Write service tokens to a file for email clients to read.
- `#8486 <https://leap.se/code/issues/8486>`_: Fetch smtp cert automatically if missing.
- `#8487 <https://leap.se/code/issues/8487>`_: Add change password command.
- `#8488 <https://leap.se/code/issues/8488>`_: Add list users to bonafide.
- Use mail_auth token in the core instead of imap/smtp tokens.


Bugfixes
~~~~~~~~
- `#8498 <https://leap.se/code/issues/8498>`_: In case of wrong url don't leave files in the config folder.

.. _`master`: https://0xacab.org/leap/bitmask-dev
