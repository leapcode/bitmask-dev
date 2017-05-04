#!/bin/bash

# Usage

set -e

PROVIDER='demo.bitmask.net'
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
"$BCTL" user create "$user" --pass "$pw"

# Authenticate
"$BCTL" user auth "$user" --pass "$pw" > /dev/null

# Enable VPN
"$BCTL" vpn enable 

# Get VPN cert
"$BCTL" vpn get_cert "$user" 

"$BCTL" vpn start

sleep 10

"$BCTL" vpn status

tests/e2e/check_ip vpn_on

"$BCTL" vpn stop

sleep 5

tests/e2e/check_ip vpn_off

echo "Succeeded - the vpn routed you through the expected address"
