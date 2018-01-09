#!/bin/bash
###########################################################
# Build a Bitmask bundle inside a fresh virtualenv (LINUX).
# To be run by Gitlab Runner,
# will produce an artifact for each build.
###########################################################

# Stop bundling in case of errors
set -e

VENV=venv

echo "[+] BUILDING BITMASK BUNDLE..."
echo "[+] GIT VERSION" `git describe`

if [ ! -d "$VENV" ]; then
  echo "[+] creating virtualenv in venv"
  virtualenv $VENV
fi
source "$VENV"/bin/activate
echo "[+] Using venv in" $VIRTUAL_ENV

$VIRTUAL_ENV/bin/pip install appdirs packaging
# qt-plugins instability in develop: see https://github.com/pyinstaller/pyinstaller/issues/1906
# $VIRTUAL_ENV/bin/pip install -U pyinstaller==3.2.1
# dev version
$VIRTUAL_ENV/bin/pip install -U git+https://github.com/pyinstaller/pyinstaller.git
$VIRTUAL_ENV/bin/pip install zope.interface zope.proxy

# fix for #8789
$VIRTUAL_ENV/bin/pip --no-cache-dir install pysqlcipher --install-option="--bundled"
# FIXME pixelated needs some things but doesn't declare it
$VIRTUAL_ENV/bin/pip install chardet
# FIXME remove requests in pixelated fork, use treq instead
$VIRTUAL_ENV/bin/pip install requests==2.11.1

# Soledad version: for the Bitmask 0.10 bundles, let's pick published soledad.
$VIRTUAL_ENV/bin/pip install -U leap.soledad
# CHANGE THIS IF YOU WANT A DIFFERENT BRANCH CHECKED OUT FOR COMMON/SOLEDAD --------------------
#$VIRTUAL_ENV/bin/pip install -U leap.soledad --find-links https://devpi.net/kali/dev 
# ----------------------------------------------------------------------------------------------

# XXX hack for the namespace package not being properly handled by pyinstaller
touch $VIRTUAL_ENV/lib/python2.7/site-packages/zope/__init__.py
touch $VIRTUAL_ENV/lib/python2.7/site-packages/leap/soledad/__init__.py

make dev-gui
make dev-mail

$VIRTUAL_ENV/bin/pip uninstall --yes leap.bitmask
$VIRTUAL_ENV/bin/python setup.py sdist bdist_wheel --universal

echo "[+] Installing Bitmask from latest wheel..."
$VIRTUAL_ENV/bin/pip install `ls -tr dist/*.whl | tail -n 1`

# Get the bundled libzmq
$VIRTUAL_ENV/bin/pip install -I pyzmq --install-option="--zmq=bundled"

# Get latest tags from repo
git fetch --tags
make bundle_linux
