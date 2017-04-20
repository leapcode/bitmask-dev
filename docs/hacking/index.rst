:LastChangedDate: $LastChangedDate$
:LastChangedRevision: $LastChangedRevision$
:LastChangedBy: $LastChangedBy$

Hacking
========================================
So you want to hack on Bitmask?
Thanks, and welcome!

Running tests
---------------------------------

Tox is all you need::

  tox

Test when changes are made to common/soledad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are developing against a non-published branch of ``leap.common`` or
``leap.soledad``, run instead::

  tox -e py27-dev

This expects ``leap_common`` and ``soledad`` repos to be checked out in the
parent folder.

Setting up the development environment
--------------------------------------

Dependencies::

  sudo apt install build-essential python-virtualenv libsqlcipher-dev \
                   libssl-dev libffi-dev python-pyqt5


Create a virtualenv and activate it::

  mkvirtualenv venv
  source venv/bin/activate

(but consider using something like `pew`_ if you are going to do heavy development
though).

Now you should be able to install all the bitmask dependencies::

  make dev-latest-all

.. _`pew`: https://pypi.python.org/pypi/pew/0.1.26

How to contribute
---------------------------------

Send your merge requests to https://0xacab/leap/bitmask-dev

Coding conventions
---------------------------------
* pep8
* Git messages should be informative.
* There is a pre-commit hook ready to be used in the ``docs/hooks`` folder,
  alongside some other hooks to do autopep8 on each commit.

.. include:: ../hooks/leap-commit-template.README
   :literal:

Pinning
----------------------------------
Don't introduce any pinning in the setup.py file, they should go in the
requirements files (mainly ``pkg/requirements.pip``).


Signing your commits
---------------------------------
* For contributors with commit access, you **should** sign all your commits. If
  you are merging some code from external contributors, you should sign their
  commits.

Merging code
---------------------------------
Avoid fast-forwards. Put this in your gitconfig::

  [merge]
  ff = only  


Main Bitmask Components
---------------------------------

The Core
~~~~~~~~

The main bitmask-dev repo orchestrates the launching if the bitmaskd daemon.
This is a collection of services that launches the vpn and mail services.
bitmask vpn, mail and keymanager are the main modules, and soledad is one of the
main dependencies for the mail service.

The Qt gui
~~~~~~~~~~

The Qt gui is a minimalistic wrapper that uses PyQt5 to launch the core and
display a qt-webkit browser rendering the resources served by the core. Its main
entrypoint is in ``gui/app.py``.

The Javascript UI
~~~~~~~~~~~~~~~~~

A modern javascript app is the main Bitmask Frontend. For instructions on how
to develop with the js ui, refer to ``ui/README.md``.

The Thunderbird Extension
~~~~~~~~~~~~~~~~~~~~~~~~~

The development for the Thunderbird Extension happens on `this repo`_.
This extension gets published to the `mozilla addons page`_.

.. _`this repo`: https://0xacab.org/leap/bitmask_thunderbird
.. _`mozilla addons page`: https://addons.mozilla.org/en-US/thunderbird/addon/bitmask


Making a new release
--------------------

A checklist for the release process can be found :ref:`here <release>`

As part of the release we also tag upload snapshots of the `leap.bitmask_js`
package, in order to allow installation of the javascript application without
needing to compile the javascript and html assets. This is done with::

   cd ui
   make dist-build

and then you can upload it to pypi::

   make dist-upload

Contribution ideas
------------------

Want to help? Come talk to us on irc or the mailing list!

Some areas in which we always need contribution are:

* Localization of the client (talk to elijah).
* Multiplatform gitlab runners
* Windows and OSX packaging (talk to kali)
* Windows Firewall integration for VPN
* Migrating components to py3 (look for vshyba or kali).
