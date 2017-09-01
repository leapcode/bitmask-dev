Bitmask
===========================================================

*Your internet encryption toolkit*

.. image:: https://badge.fury.io/py/leap.bitmask.svg
    :target: http://badge.fury.io/py/leap.bitmask
.. image:: https://0xacab.org/leap/bitmask-dev/badges/master/build.svg
    :target: https://0xacab.org/leap/bitmask-dev/pipelines
.. image:: https://readthedocs.org/projects/bitmask/badge/?version=latest
   :target: http://bitmask.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. image:: https://img.shields.io/badge/IRC-leap-blue.svg
   :target: http://webchat.freenode.net/?channels=%23leap&uio=d4
   :alt: IRC
.. image:: https://img.shields.io/badge/IRC-bitmask_(es)-blue.svg
   :target: http://webchat.freenode.net/?channels=%23bitmask-es&uio=d4
   :alt: IRC-es


**Bitmask** is the client for the services offered by `the LEAP Platform`_. It
contains a command-line interface and a multiplatform desktop client. It can be
also used as a set of libraries to communicate with the different services from
third party applications.

It is written in python using `Twisted`_  and licensed under the `GPL3`_. The
Graphical User Interface is written in html+js and uses `PyQt5`_ for serving
the application.

.. _`the LEAP Platform`: https://github.com/leapcode/leap_platform
.. _`Twisted`: https://twistedmatrix.com
.. _`PyQt5`: https://pypi.python.org/pypi/PyQt5
.. _`GPL3`: http://www.gnu.org/licenses/gpl.txt

Package under development!
-----------------------------------------------------------

The previous client using PySide has been deprecated (Bitmask version 0.9.2,
still available at the http://github.com/leapcode/bitmask_client repo).


Read the Docs!
-----------------------------------------------------------

There is documentation about Bitmask `for users`_ and `for developers`_.

.. _`for users`: https://leap.se/en/docs/client
.. _`for developers`: https://bitmask.rtfd.io

Bugs
===========================================================

Please report any bugs `in our bug tracker`_.

.. _`in our bug tracker`: https://0xacab.org/leap/bitmask-dev/issues/

Logs
----

If you want to watch the logs, from the command line::

  bitmaskctl logs watch

The paste command can be handy to do bug reports (needs ``pastebinit`` installed
in the system)::

  bitmaskctl logs send


Development
===========================================================

Running Tests
-----------------------------------------------------------

You need tox to run the tests. If you don't have it in your system yet::

  pip install tox

And then run all the python tests::

  tox

There are some minimal end-to-end tests::

  make test_e2e

For testing the UI (aka ``bitmask-js``) you need to have ``mocha``
installed. You can run ui tests like this::

  cd ui && make test


Hacking
-----------------------------------------------------------

In order to run bitmask in a development environment, you must activate a
virtualenv and install the various packages using 'pip install -e'. This
installs python packages as links to the source code, so that your code
changes are immediately reflected in the packages installed in the
virtualenv.

The various ``make dev-*`` commands will run the appropriate ``pip install``
commands for you.

If you want to setup your whole development environment, and you are running a
debian-based system, you can try::

  make dev-bootstrap

To upgrade regularly the python dependencies installed inside your virtualenv,
you can run::

  make upgrade-all

inside your virtualenv, and it will install any new version of your
dependencies that is found in pypi.


Run headless backend in development mode
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Prerequisites::

  sudo apt install build-essential python-dev python-virtualenv \
                   libsqlcipher-dev libssl-dev libffi-dev

Install and activate a virtualenv::

  cd bitmask-dev
  virtualenv venv
  source venv/bin/activate

(Refer to the `virtualenv documentation` if you're not using bash/zsh/dash).

All the subsequent commands assume that you have activated the virtualenv.

Install all the python dependencies::

  make dev-backend

Run application::

  bitmaskd

.. _`virtualenv documentation`: https://virtualenv.pypa.io/en/stable/userguide/#activate-script

Run user interface frontend
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

If you want to run the Bitmask user interface, you additionally need the
following:

Prerequisites::

  sudo apt install python-pyqt5  python-pyqt5.qtwebkit

Install python dependencies::

  make dev-all

Note: even though the UI is in javascript, Qt is used to create a webview
window.

Run user interface::

  bitmask

The command `bitmask` should be in your path if you have activated the virtual
environment.

Install Bitmask user interface in development mode
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The above instructions will install a python package that contains a pre-
bundled version of the javascript UI.

If you want to modify the javascript UI, then you need to be able to update the
javascript bundle whenever a javascript or CSS source file changes. To support
this, we build a python package of the javascript UI and install it in
"development mode" so that changes to the contents of the package are reflected
in bitmaskd immediately.

Prerequisites::

  sudo apt install nodejs npm nodejs-legacy

Next, run ``dev-install``::

  cd ui
  make dev-install

Now you should be able to run the user interface with debugging tools::

  bitmaskd
  cd ui
  npm run ui

This command is the same as running::

  chromium-browser "http://localhost:7070/#$(cat ~/.config/leap/authtoken)"

Firefox does not work as well, because the UI is only tested with webkit-based
browsers.

Chromium is not the most ideal, however, because it uses a newer webkit than is
available in Qt. Instead, try qupzilla::

  sudo apt install qupzilla
  bitmaskd
  qupzilla -ow "http://localhost:7070/#$(cat ~/.config/leap/authtoken)"

If you make a change to any of the CSS or JS source files, you need to rebuild
the javascript bundle. You can do this continually as files change like so::

  cd ui
  node run watch

The new javascript bundle will be used when you refresh the page so long as
``make dev-install`` was previously run.

For more information, see ``ui/README.md``.

License
===========================================================

.. image:: https://raw.github.com/leapcode/bitmask_client/develop/docs/user/gpl.png

Bitmask is released under the terms of the `GNU GPL version 3`_ or later.

.. _`GNU GPL version 3`: http://www.gnu.org/licenses/gpl.txt
