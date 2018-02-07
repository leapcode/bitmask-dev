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

Gateway failures
-----------------------------------

If Bitmask VPN fails to connect to one gateway it will try with the next
following gateway selection order.

In case of connection loss Bitmask will keep trying to connect to each of the
gateways again and again until the connection comes back. When the connection
is back Bitmask will connect to the gateway that was trying at the moment.
In practice after a reconnection the gateway that Bitmask gets connected is
practically random.

Turning the VPN down and up again after a reconnection ensures that Bitmask
will try again the first gateway.

In the future Bitmask should become more in control of the reconnect process,
that currently is handled by openvpn, and detect reconnections to select the
gateways better.

Autostart
---------
Autostart is not implemented yet in the 0.10 versions of Bitmask, but you can probably use 
a systemd script to launch vpn. If you have the latest master installed from a debian package::

  [Unit]
  Description=Bitmask VPN
  Documentation=https://bitmask.net/en/help

  [Service]
  Type=oneshot
  WorkingDirectory=/var/run/bitmask

  ExecStart=bitmaskctl vpn start demo.bitmask.net
  ExecStop=bitmaskctl vpn stop

  RemainAfterExit=yes

  [Install]
  WantedBy=default.target

Another option is to autostart it adding a ``~/.config/autostart/bitmask.desktop``::

  [Desktop Entry]
  Version=1.0
  Encoding=UTF-8
  Type=Application
  Name=Bitmask
  Comment=Secure Communication
  Exec=bitmaskctl vpn start
  Terminal=false
  Icon=bitmask

Qubes i3 status
---------------
The following script can be used to add the bitmask status to the i3 status bar in qubes::

  status_bitmask() {
      local status=$(qvm-run "sys-bitmask" -p 'bitmaskctl vpn status --json' 2>/dev/null)
      local error=$(parse_json 'error')
  
      if [[ $error -ne "None" ]]; then
          json bitmask "VPN: $error" '#ff0000'
      else
          local domain=$(parse_json 'result' 'domain')
          local sttus=$(parse_json 'result' 'status')
          local up=$(parse_json 'result' 'up')
          local down=$(parse_json 'result' 'down')
          local error=$(parse_json 'result' 'error')
  
          case $sttus in
              "on")
                  local text="$domain: ↑$up ↓$down"
                  local color=""
                  ;;
              "starting")
                  local text="$domain: starting"
                  local color="#00ff00"
                  ;;
              "off"|"stopping")
                  local text="VPN: off"
                  local color='#ffff00'
                  ;;
              "failed")
                  local text="VPN: $error"
                  local color="#ff0000"
                  ;;
          esac
          json bitmask "$text" $color
      fi
  }
  
  parse_json() {
      local item=""
      for param in $@; do
          item=${item}"['${param}']"
      done
      echo -n $(python -c "import json; j=json.loads(\"\"\"$status\"\"\"); print j${item}")
  }
