# -*- mode: python -*-
import os
import sys
import platform

block_cipher = None

IS_MAC = sys.platform.startswith('darwin')
IS_WIN = platform.system() == 'Windows'

BITMASK_VERSION = open('pkg/next-version').read()
if IS_MAC:
    # launchd chokes because more digits are added to the version string,
    # so let's skip the patch part of the version.
    BITMASK_VERSION  = '.'.join(BITMASK_VERSION.split('.')[:-1])

hiddenimports = [
     'appdirs',
     'service_identity',
     'leap.common', 'leap.bitmask', 
     'leap.bitmask.core.logs',
     'packaging', 'packaging.version', 'packaging.specifiers',
     'packaging.requirements']

VENV = os.environ.get('VIRTUAL_ENV', '')
ENTRYPOINT = ['../../src/leap/bitmask/gui/anonvpn.py']

a = Analysis(ENTRYPOINT,
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
          name='anonvpn',
          debug=True,
          strip=True,
          upx=True,
	  # TODO remove console for win
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='anonvpn')
