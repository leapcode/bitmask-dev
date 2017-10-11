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
     'scrypt._scrypt',
     'scrypt', 'zope.interface', 'zope.proxy',
     'pysqlcipher', 'service_identity',
     'leap.common', 'leap.bitmask', 
     'leap.bitmask.core.logs',
     'leap.soledad.common', 
     'leap.soledad.common.document', 
     'leap.soledad.common.l2db',
     'leap.soledad.client.events',
     'packaging', 'packaging.version', 'packaging.specifiers',
     'packaging.requirements']

excludes = ['PyQt5', 'IPython', 'PySide']
VENV = os.environ.get('VIRTUAL_ENV', '')
ENTRYPOINT = ['../../src/leap/bitmask/core/launcher.py']

a = Analysis(ENTRYPOINT,
             pathex=[
	         '/usr/lib/python2.7/dist-packages/'],
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
          name='bitmask-nox',
          debug=True,
          strip=False,
          upx=True,
	  # TODO remove console for win
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='bitmask-nox')
