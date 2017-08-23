import os
import sys

import pip
from subprocess import call

if not os.environ.get('VIRTUAL_ENV'):
    print('[!] Should call this script inside a virtualenv, I do not want to '
          'mess with your system. Bye!')
    sys.exit(1)

for dist in pip.get_installed_distributions():
    call("pip install --upgrade " + dist.project_name, shell=True)
