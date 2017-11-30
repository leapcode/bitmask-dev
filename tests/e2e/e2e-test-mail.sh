#!/bin/bash

# Dependencies
# - swaks and uuid-runtime debian packages
#
#
# Usage
#
# In order to send authenticated mail to the tmp_user you need to
# export these environment variables before running this script:
#   - FROM_EXTERNAL_OPTS for sending mails from external mailservers to the tmp_user account
#
# as an example:
#   export FROM_EXTERNAL_OPTS='--tlsc --au user@example.or -ap MYPASSWORD -s smtp.example.org'
#
# then:
#
#   source venv/bin/activate
#   make dev-latest-backend
#   make test_e2e
#
#
# TODO:
#   - Timeout waiting for mail
#   - Decrease poll interval
#   - Make it less noisy (fix the vext warnings)
#   - move away from cdev.bm
#   - remove test user on success

# exit if any commands returns non-zero status
set -e

# DEBUG
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

PROVIDER='ci.leap.se'

BCTL='bitmaskctl'
LEAP_HOME="$HOME/.config/leap"
MAIL_UUID=$(uuidgen)

username="tmp_user_$(date +%Y%m%d%H%M%S)"
user="${username}@${PROVIDER}"
set +x  # Disable xtrace
pw="$(head -c 10 < /dev/urandom | base64)"
INVITE_CODE=${BITMASK_INVITE_CODE:?"Need to set BITMASK_INVITE_CODE non-empty"}
[[ $xtrace == true ]] && set -x  # Enable xtrace again only if it was set at beginning of script

SWAKS="swaks --h-Subject $MAIL_UUID --silent 2 -s ${PROVIDER} --helo leap.se -f ci@leap.se -t $user"

# Stop any previously started bitmaskd
# and start a new instance
"$BCTL" stop

[ -d "$LEAP_HOME" ] && rm -rf "$LEAP_HOME"

# XXX skip certificate verification! -- self-signed cert in ci.leap.se
SKIP_TWISTED_SSL_CHECK=1 "$BCTL" start

# Show bitmaskd logs
# tail -F "${LEAP_HOME}/bitmaskd.log" &

# Register a new user
# Disable xtrace
set +x
"$BCTL" user create "$user" --pass "$pw" --invite "$INVITE_CODE"
# Enable xtrace again only if it was set at beginning of script
[[ $xtrace == true ]] && set -x

#tail ~/.config/leap/bitmaskd.log
echo "created user. authenticating..."

# Authenticate
# Disable xtrace
set +x
"$BCTL" user auth "$user" --pass "$pw" > /dev/null
# Enable xtrace again only if it was set at beginning of script
[[ $xtrace == true ]] && set -x

# Note that imap_pw is the same for smtp

imap_pw="None"

# FIXME -- this would be prettier if we had the auth command block on
# the first-time run, so that we just return when the key has been generated
# and explicitely raise any error found

while [[ $imap_pw == *"None"* ]]; do
  response=$("$BCTL" mail get_token)
  sleep 10
  imap_pw=$(echo "$response" | head -n 1 | sed 's/  */ /g' | cut -d' ' -f 2)
done

$SWAKS $FROM_EXTERNAL_OPTS


echo "IMAP/SMTP PASSWD: $imap_pw"

# Send testmail
$SWAKS $FROM_EXTERNAL_OPTS

# wait until we the get mail we just sent.
while ! ./tests/e2e/getmail --mailbox INBOX --subject "$MAIL_UUID" "$user" "$imap_pw" > /dev/null
do
  echo "Waiting for incoming test mail..."
  sleep 10
done

echo -e "Succeeded - mail arrived\n\n\n"
