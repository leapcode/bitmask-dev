#!/bin/bash

# Usage
# ...

# exit if any commands returns non-zero status
set -e

# XXX DEBUG
set -x

# Check if scipt is run in debug mode so we can hide secrets
if [[ "$-" =~ 'x' ]]
then
  echo 'Running with xtrace enabled!'
  xtrace=true
else
  echo 'Running with xtrace disabled!'
  xtrace=false
fi

PROVIDER='demo.bitmask.net'
INVITE_CODE=${BITMASK_INVITE_CODE:?"Need to set BITMASK_INVITE_CODE non-empty"}
BCTL='bitmaskctl'
LEAP_HOME="$HOME/.config/leap"

username="tmp_user_$(date +%Y%m%d%H%M%S)"
user="${username}@${PROVIDER}"
pw="$(head -c 10 < /dev/urandom | base64)"

# Stop any previously started bitmaskd
# and start a new instance
"$BCTL" stop

[ -d "$LEAP_HOME" ] && rm -rf "$LEAP_HOME"

"$BCTL" start


# Register a new user
# Disable xtrace
set +x
"$BCTL" user create "$user" --pass "$pw" --invite "$INVITE_CODE"
# Enable xtrace again only if it was set at beginning of script
[[ $xtrace == true ]] && set -x

# Authenticate
"$BCTL" user auth "$user" --pass "$pw" > /dev/null

# Enable VPN
"$BCTL" vpn enable 

# Get VPN cert
"$BCTL" vpn get_cert "$user" 

"$BCTL" vpn start --json

# XXX DEBUG ---
tail -n 200  ~/.config/leap/bitmaskd.log
which pkexec
ls -la /usr/sbin/openvpn
ls -la /usr/local/sbin/bitmask-root
# XXX DEBUG ---

sleep 5

"$BCTL" vpn status --json

tests/e2e/check_ip vpn_on

"$BCTL" vpn stop

sleep 5

tests/e2e/check_ip vpn_off

echo "Succeeded - the vpn routed you through the expected address"
