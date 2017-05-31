VPN port
--------
What's here is a simple port of the legacy bitmask_client vpn code::

  bitmaskctl user create tmp_user_baz002@demo.bitmask.net --pass 1234
  signup    ok
  user      tmp_user_baz002

  bitmaskctl user auth tmp_user_baz002@demo.bitmask.net --pass 1234
  srp_token iye7s1J7M3_iCdB4gXEAhxs-if3XOCwpKNPnvTC8ycE
  uuid      b63ac83826c7e1e903ed18f6f7780491

  bitmaskctl vpn get_cert
  get_cert  ok

  bitmaskctl vpn check
  vpn_ready ok


You also might want to install the helpers (a pop-up should appear, asking for
authentication)::

  bitmaskctl vpn install
  install   ok

And finally you should be able to launch the VPN::

  bitmaskctl vpn start
  start     ok
  result    started

  bitmaskctl vpn status
  firewall  ON
  vpn       AUTH

  bitmaskctl vpn status
  firewall  ON
  vpn       CONNECTED
  ↑↑↑       11.3 K
  ↓↓↓       3.9 K


Feedback needed
---------------
Much of what's exposed in the above API should be made transparently (download
certificate). However, I prefer to test it manually before hiding it from the
CLI.

0.10 version uses this basic API, further releases will automate getting the
certificates, validation, renewal etc.

Please report any bugs you find with its expected behavior, either using the cli
or the gui.
