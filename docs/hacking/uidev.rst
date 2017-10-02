.. _uidev:

Bitmask's Javascript User Interface
====================================

Some notes specific to development of the javascript ui interface. For more detail, see ``ui/README.md``.

Run headless backend in development mode
----------------------------------------

Prerequisites::

.. note: move this snippet to a common include!

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
---------------------------

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
--------------------------------------------------

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
