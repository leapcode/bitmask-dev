#!/bin/bash

# Usage
# ...

# exit if any commands returns non-zero status
set -e

# ONLY ENABLE THIS TO DEBUG
# set -x

# Check if scipt is run in debug mode so we can hide secrets
if [[ "$-" =~ 'x' ]]
then
  echo 'Running with xtrace enabled!'
  xtrace=true
else
  echo 'Running with xtrace disabled!'
  xtrace=false
fi

PROVIDER='ci.leap.se'
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

# Register a new user
# Disable xtrace
set +x
"$BCTL" user create "$user" --pass "$pw" --invite "$INVITE_CODE"
# Enable xtrace again only if it was set at beginning of script
[[ $xtrace == true ]] && set -x

# Authenticate
"$BCTL" user auth "$user" --pass "$pw" > /dev/null

# Get VPN cert
"$BCTL" vpn get_cert "$user" 

# Start VPN, wait a bit
"$BCTL" vpn start --json
sleep 5
"$BCTL" vpn status --json

if [[ $EUID > 0 ]]
  then echo "Not running as root, no dns workaround needed...";
else
  echo "no-iptables workaround on CI: adding gateway dns...";
  echo "nameserver 10.42.0.1" > /etc/resolv.conf
  # cat /etc/resolv.conf
fi

sleep 5

ip link show
cat ~/.config/leap/bitmaskd.log

# TEST that we're going through the provider's VPN
tests/e2e/check_ip vpn_on

"$BCTL" vpn stop
sleep 5

if [[ $EUID > 0 ]]
  then echo "Not running as root, no dns workaround needed...";
else
  echo "no-iptables workaround on CI: restoring dns...";
  echo "nameserver 77.109.148.136" > /etc/resolv.conf
fi


# TEST that we're NOT going through the provider's VPN
tests/e2e/check_ip vpn_off

echo "Succeeded - the vpn routed you through the expected address"
