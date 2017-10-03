.. _issues:

===================
Known Issues
===================

VPN
-------------------

* If there's no running polkit agent in the system, the UI hangs in the 'Connecting' State. (solution: install and run some agent, like ``lxpolkit``).
* Some problems with resuming after hibernation (more debug info is welcome).

Wizard
-------------------

* In the wizard log in / sign up page, the username field gets deselected.
* The list of providers should have icons, be sortable, filterable.
* The wizard should look more pretty.

Main window
-------------------

* UI doesn't subscribe to events yet, won't get updated if user has logged out
  via the command line interface.
* Removing an account does not actually clean up all the files associated with
  that account (need backend code).
* `#8840 <https://0xacab.org/leap/bitmask-dev/issues/8840>`_: No ability to recover if the key generation fails.

Pixelated Integration
---------------------
The integration of the Pixelated webmail is a bit rough at the moment.

Particularly, simultaneous use of Pixelated and Thunderbird is likely to hit some usability issues:

* `#8905 <https://0xacab.org/leap/bitmask-dev/issues/8905>`_: pixelated: if a message is open in Thunderbird, the unread count is not updated
* `#8906 <https://0xacab.org/leap/bitmask-dev/issues/8906>`_: pixelated: can't see messages that were sent with Thunderbird
* Pixelated MUA is not authenticated.

