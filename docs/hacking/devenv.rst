.. _devenv:

Setting a Development Environment
=================================

Convenience script
------------------

There is an automated script that runs, sequentially, all the commands in the
section below. In debian-based systems, you can get a fully working development
environment with::

  make dev-bootstrap

To activate the freshly created virtualenv the next time, you must use `pew`_::

  pew workon bitmask

.. note:: the bootstrap script is, at the moment, quite opinionated. for
          instance, it installs and depends on pew, it checks out the
          bitmask-dev repo under ~/leap folder, and it assumes you are using
          zsh. if you think it should allow more freedom of choices, feel free
          to open a pull request.

.. _`pew`: https://pypi.python.org/pypi/pew

Manual instructions 
-------------------

Install the system-wide dependencies. For debian-based systems::

  sudo apt install build-essential python-dev python-virtualenv \
  libsqlcipher-dev libssl-dev libffi-dev \
  python-pyqt5 python-pyqt5.qtwebkit

If you are going to be running tests that involve creating a lot of OpenPGP
keys, and specially in vms, the following is also recommended to speed up
things::

  sudo apt install haveged


Clone the repo. The master branch has the latest code::

  git clone https://0xacab.org/leap/bitmask-dev
  cd bitmask-dev

Create a virtualenv and activate it::

  virtualenv venv
  source venv/bin/activate

By the way, if you plan to get into heavy development, you might want to
consider using something like `pew`_, instead of the plain virtualenv.

Now you should be able to install all the bitmask dependencies::

  make dev-latest-all

You can also install some dependencies that are going to be useful during
development::

  pip install -r pkg/requirements-dev.pip

What next?
-----------
Check out the Bitmask Architecture.
