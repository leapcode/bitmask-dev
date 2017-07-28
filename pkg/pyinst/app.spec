# -*- mode: python -*-
import platform
import sys

block_cipher = None

IS_MAC = sys.platform.startswith('darwin')

BITMASK_VERSION = open('pkg/next-version').read()
if IS_MAC:
    # launchd chokes because more digits are added to the version string,
    # so let's skip the patch part of the version.
    BITMASK_VERSION  = '.'.join(BITMASK_VERSION.split('.')[:-1])

hiddenimports = [
     'appdirs',
     'scrypt', 'zope.interface', 'zope.proxy',
     'leap.pixelated_www', 'pixelated', 'chardet', 'whoosh', 'requests',
     'pysqlcipher', 'service_identity',
     'leap.common', 'leap.bitmask', 
     'leap.bitmask.core.logs',
     'leap.bitmask.gui.icons_rc',
     'leap.soledad.common', 
     'leap.soledad.common.document', 
     'leap.soledad.common.l2db',
     'leap.soledad.client.events',
     'leap.bitmask_js',
     'packaging', 'packaging.version', 'packaging.specifiers',
     'packaging.requirements']

if platform.system() == 'Windows':
    print "Platform=Windows, using pyside..."
    hiddenimports.extend(
        ['PySide.QtCore', 'PySide.QtGui', 'PySide.QtWebKit',
	# for some reason pyinstaller 3.1 complains about missing
	# packages that should have been vendored
	'appdirs',
	'packaging', 'packaging.version', 'packaging.specifiers',
	'packaging.requirements',
	'python-gnupg'])
    excludes = ['PyQt5']
else:
    hiddenimports.extend(
        ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWebKit'])
    excludes = ['PySide']

import os
VENV = os.environ.get('VIRTUAL_ENV', '')

a = Analysis(['../../src/leap/bitmask/gui/app.py'],
             pathex=[
	         '/usr/lib/python2.7/dist-packages/',
	        VENV + '/Lib/site-packages/',
	        VENV + '/Lib/site-packages/leap/soledad'],
             binaries=None,
             datas=None,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=excludes,

             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='bitmask',
          debug=False,
          strip=False,
          upx=True,
	  # TODO remove console for win
          console=True,
          icon='../branding/mask-icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='bitmask')

if IS_MAC:
    app = BUNDLE(
    	coll,
        name=os.path.join(
          'dist', 'Bitmask.app'),
          appname='Bitmask',
          version=BITMASK_VERSION,
          icon='pkg/osx/bitmask.icns',
	  bundle_identifier='bitmask-' + BITMASK_VERSION)
