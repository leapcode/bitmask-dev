:LastChangedDate: $LastChangedDate$
:LastChangedRevision: $LastChangedRevision$
:LastChangedBy: $LastChangedBy$

.. _vpn:


Bitmask VPN
================================

The Bitmask VPN Module

Gateway Selection
-----------------------------------

By default, the Gateway Selector will apply a heuristic based on the configured
timezone of the system.  This will choose the closest gateway based on the
timezones that the provider states in the ``eip-config.json`` file.

If the locations section is not properly set by the provider, or if the user
wants to manually override the selection, the only way to do this for the
``0.10`` version of Bitmask is to add a section to the ``bitmaskd.cfg``
configuration file::

  [vpn]
  locations = ["rio__br"]
  countries = ["BR", "AR", "UY"]

Take into account that the locations entry has precedence over the country codes enumeration.

Also, the normalization is done so that any non-alphabetic character is substituted by an underscore ('``_``).

You can list all the configured locations using the CLI::

  % bitmaskctl vpn list
  demo.bitmask.net      [DE] Frankfurt (UTC+1)
  demo.bitmask.net      [US] Seattle, WA (UTC-7)

This manual override functionality will be exposed through the UI and the CLI in release ``0.11``.
