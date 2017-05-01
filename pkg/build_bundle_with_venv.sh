#!/bin/bash
###########################################################
# Build a Bitmask bundle inside a fresh virtualenv.
# To be run by Gitlab Runner,
# will produce an artifact for each build.
###########################################################
# Stop bundling in case of errors
set -e
virtualenv venv
source venv/bin/activate
$VIRTUAL_ENV/bin/pip install appdirs packaging
# $VIRTUAL_ENV/bin/pip install -U pyinstaller==3.1
$VIRTUAL_ENV/bin/pip install -U pyinstaller
$VIRTUAL_ENV/bin/pip install zope.interface zope.proxy

# fix for #8789
$VIRTUAL_ENV/bin/pip --no-cache-dir install pysqlcipher --install-option="--bundled"
# FIXME pixelated needs some things but doesn't declare it
$VIRTUAL_ENV/bin/pip install chardet whoosh
# FIXME persuade pixelated to stop using requests in favor of treq
$VIRTUAL_ENV/bin/pip install requests==2.11.1

# For the Bitmask 0.9.5 bundles.
#$VIRTUAL_ENV/bin/pip install -U leap.soledad.common==0.9.5
#$VIRTUAL_ENV/bin/pip install -U leap.soledad.client==0.9.5

# CHANGE THIS IF YOU WANT A DIFFERENT BRANCH CHECKED OUT FOR COMMON/SOLEDAD --------------------
$VIRTUAL_ENV/bin/pip install -U leap.soledad.common --find-links https://devpi.net/kali/dev 
$VIRTUAL_ENV/bin/pip install -U leap.soledad.client --find-links https://devpi.net/kali/dev 
# ----------------------------------------------------------------------------------------------

# XXX hack for the namespace package not being properly handled by pyinstaller
touch $VIRTUAL_ENV/lib/python2.7/site-packages/zope/__init__.py
touch $VIRTUAL_ENV/lib/python2.7/site-packages/leap/soledad/__init__.py

make dev-gui
make dev-mail

$VIRTUAL_ENV/bin/pip uninstall --yes leap.bitmask
$VIRTUAL_ENV/bin/python setup.py sdist bdist_wheel --universal
$VIRTUAL_ENV/bin/pip install dist/*.whl

# install pixelated from kali dev repo until assets get packaged.
pip install pixelated-www pixelated-user-agent --find-links https://downloads.leap.se/libs/pixelated/

make bundle
make bundle_apps
