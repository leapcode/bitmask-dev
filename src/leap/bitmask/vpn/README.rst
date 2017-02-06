VPN port
--------
What's here is a quick port of the legacy bitmask_client vpn code.
It only work through the cli right now::

  bitmaskctl user create tmp_user_baz002@demo.bitmask.net --pass 1234
  signup    ok
  user      tmp_user_baz002

  bitmaskctl user auth tmp_user_baz002@demo.bitmask.net --pass 1234
  srp_token iye7s1J7M3_iCdB4gXEAhxs-if3XOCwpKNPnvTC8ycE
  uuid      b63ac83826c7e1e903ed18f6f7780491

  bitmaskctl eip get_cert demo.bitmask.net
  get_cert  ok

  bitmaskctl eip check
  eip_ready ok


You also might want to install the helpers (a pop-up should appear, asking for
authentication)::

  bitmaskctl eip install
  install   ok

And finally you should be able to launch the VPN::

  bitmaskctl eip start demo.bitmask.net
  start     ok
  result    started

  bitmaskctl eip status
  firewall  ON
  EIP       AUTH

  bitmaskctl eip status
  firewall  ON
  EIP       CONNECTED
  ↑↑↑       11.3 K
  ↓↓↓       3.9 K


Feedback needed
---------------
Much of what's exposed in the above API should be made transparently (download
certificate). However, I prefer to test it manually before hiding it from the
CLI.

The UI integration should follow soon.

Meanwhile, please report any bugs you find with its expected behavior.
