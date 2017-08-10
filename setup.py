"""
Setup file for leap.bitmask
"""
from setuptools import setup, find_packages
import platform

import versioneer


# This requirements list is curated by hand, and
# needs to be updated every time that requirements.pip
# changes.
# Note that here we can specify ranges.

required = [
    'twisted>=14.0.0',
    'cryptography',
    'zope.interface',
    'service-identity',
    'colorama',
    'srp',
    'python-daemon',
    'certifi',
    'leap.common',
]

if platform.system() == "Windows":
    required.append(['pypiwin32'])
    required.append(['appdirs'])
    required.append(['python-gnupg'])

mail_deps = ['leap.soledad[client]', 'gnupg']
pix_deps = ['leap.pixelated', 'leap.pixelated_www']
gui_deps = ['vext.pyqt5', 'leap.bitmask_js']
tor_deps = ['txtorcon']
extras = {
    'mail': mail_deps,
    'pixelated': pix_deps,
    'gui': gui_deps,
    'backend': mail_deps,
    'all': mail_deps + gui_deps + pix_deps,
    'tor': tor_deps
}


trove_classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: End Users/Desktop",
    ("License :: OSI Approved :: GNU General "
     "Public License v3 or later (GPLv3+)"),
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Topic :: Communications",
    'Topic :: Communications :: Email',
    "Topic :: Security",
    'Topic :: Security :: Cryptography',
    "Topic :: Utilities"
]

VERSION = versioneer.get_version()
DOWNLOAD_BASE = ('https://github.com/leapcode/bitmask-dev/'
                 'archive/%s.tar.gz')
DOWNLOAD_URL = DOWNLOAD_BASE % VERSION


# Entry points
gui_launcher = 'bitmask=leap.bitmask.gui.app:start_app'
chrome_launcher = 'bitmask_chromium=leap.bitmask.chrome.chromeapp:start_app'
bitmask_cli = 'bitmaskctl=leap.bitmask.cli.bitmask_cli:main'
bitmask_helpers = 'bitmask_helpers=leap.bitmask.vpn.helpers:main'
bitmaskd = 'bitmaskd=leap.bitmask.core.launcher:run_bitmaskd'


setup(
    name='leap.bitmask',
    version=VERSION,
    cmdclass=versioneer.get_cmdclass(),
    url='https://leap.se/',
    download_url=DOWNLOAD_URL,
    license='GPLv3+',
    author='The LEAP Encryption Access Project',
    author_email='info@leap.se',
    maintainer='Kali Kaneko',
    maintainer_email='kali@leap.se',
    description=("The Internet Encryption Toolkit: "
                 "Encrypted Internet Proxy and Encrypted Mail."),
    long_description=open('README.rst').read(),
    classifiers=trove_classifiers,
    namespace_packages=['leap'],
    package_dir={'': 'src'},
    package_data={'': ['*.pem', '*.bin']},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            gui_launcher,
            chrome_launcher,
            bitmask_cli,
            bitmaskd,
            bitmask_helpers]
    },
    install_requires=required,
    extras_require=extras,
)
