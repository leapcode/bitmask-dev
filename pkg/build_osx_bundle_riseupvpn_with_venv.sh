#!/bin/bash
###########################################################
# Build a RiseupVPN bundle inside a fresh virtualenv (OSX).
###########################################################

# Stop bundling in case of errors
set -e

VENV=venv

echo "[+] BUILDING RiseupVPN BUNDLE..."
echo "[+] GIT VERSION" `git describe`

if [ ! -d "$VENV" ]; then
  echo "[+] creating virtualenv in venv"
  virtualenv $VENV
fi
source "$VENV"/bin/activate
echo "[+] Using venv in" $VIRTUAL_ENV

$VIRTUAL_ENV/bin/pip install -U pyinstaller
$VIRTUAL_ENV/bin/pip install zope.interface zope.proxy

$VIRTUAL_ENV/bin/pip install -r pkg/requirements-osx.pip

# Get the bundled libzmq
$VIRTUAL_ENV/bin/pip install -I pyzmq --install-option="--zmq=bundled"

# Install bitmask in development mode
$VIRTUAL_ENV/bin/pip install -e .

# Get latest tags from repo
git fetch --tags
make bundle_anonvpn_osx
