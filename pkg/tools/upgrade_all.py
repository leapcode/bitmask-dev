import os
import sys

import pip
from subprocess import call

if not os.environ.get('VIRTUAL_ENV'):
<<<<<<< HEAD
    print('[!] Should call this script inside a virtualenv, I do not want to '
          'mess with your system. Bye!')
=======
    print('[!] Should call this script inside a virtualenv, I do not want to mess '
          'with your system. Bye!')
>>>>>>> 135aa3ac... [docs] add ability to upgrade an existing virtualenv
    sys.exit(1)

for dist in pip.get_installed_distributions():
    call("pip install --upgrade " + dist.project_name, shell=True)
