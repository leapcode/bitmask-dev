#!/bin/bash
###########################################################
# Build a Bitmask bundle inside a fresh virtualenv (LINUX).
# To be run by Gitlab Runner,
# will produce an artifact for each build.
###########################################################
# Stop bundling in case of errors
set -e

echo "BUILDING BITMASK BUNDLE..."
git describe

virtualenv venv
source venv/bin/activate
$VIRTUAL_ENV/bin/pip install appdirs packaging
# $VIRTUAL_ENV/bin/pip install -U pyinstaller==3.1
$VIRTUAL_ENV/bin/pip install -U pyinstaller
$VIRTUAL_ENV/bin/pip install zope.interface zope.proxy

# fix for #8789
$VIRTUAL_ENV/bin/pip --no-cache-dir install pysqlcipher --install-option="--bundled"
# FIXME pixelated needs some things but doesn't declare it
$VIRTUAL_ENV/bin/pip install chardet
# FIXME persuade pixelated to stop using requests in favor of treq
$VIRTUAL_ENV/bin/pip install requests==2.11.1

# For the Bitmask 0.10 bundles.
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
$VIRTUAL_ENV/bin/pip install dist/*.whl

pip install leap.pixelated-www leap.pixelated

# Get the bundled libzmq
$VIRTUAL_ENV/bin/pip uninstall --yes pyzmq
$VIRTUAL_ENV/bin/pip install pyzmq --install-option="--zmq=bundled"

make bundle_linux
