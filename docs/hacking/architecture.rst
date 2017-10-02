.. _architecture:

The Bitmask Architecture
========================

The Core
--------

The main bitmask-dev repo orchestrates the launching if the bitmaskd daemon.
This is a collection of services that launches the vpn and mail services.
bitmask vpn, mail and keymanager are the main modules, and soledad is one of the
main dependencies for the mail service.

The Qt gui
----------

The Qt gui is a minimalistic wrapper that uses PyQt5 to launch the core and
display a qt-webkit browser rendering the resources served by the core. Its main
entrypoint is in ``gui/app.py``.

The Javascript UI
-----------------

A modern javascript app is the main Bitmask Frontend. For instructions on how
to develop with the js ui, refer to :ref:`how to develop for the UI<uidev>`.


The Thunderbird Extension
~~~~~~~~~~~~~~~~~~~~~~~~~

The development for the Thunderbird Extension happens on `this repo`_.
This extension gets published to the `mozilla addons page`_.

.. _`this repo`: https://0xacab.org/leap/bitmask_thunderbird
.. _`mozilla addons page`: https://addons.mozilla.org/en-US/thunderbird/addon/bitmask


What Next?
----------

Have a look at the contribution guide.
