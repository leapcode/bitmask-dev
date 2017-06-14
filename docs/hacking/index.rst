:LastChangedDate: $LastChangedDate$
:LastChangedRevision: $LastChangedRevision$
:LastChangedBy: $LastChangedBy$

Hacking
========================================

So you want to hack on Bitmask?
Thanks, and welcome!

This document assumes a ``Linux`` environment.

There are also ongoing documents with notes for setting up an :ref:`osx <osx-dev>` and a
:ref:`windows <win-dev>` working environments too, contribution is very much
welcome on those docs!

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

.. _devenv:

Setting up the development environment
--------------------------------------

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


.. _`pew`: https://pypi.python.org/pypi/pew


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

Debugging Bitmask
---------------------------------

A must-read for debugging the Bitmask Core daemon is the :ref:`manhole HowTo <manhole>`.


Bitmask privileged runner
----------------------------------

For launching VPN and the firewall, Bitmask needs to run with administrative
privileges.  In linux, ``bitmask_root`` is the component that runs with root
privileges. We currently depend on ``pkexec`` and ``polkit`` to execute it as
root. In order to do that, Bitmask needs to put some policykit helper files in a
place that is root-writeable.

If you have installed Bitmask from some distro package, these folders should be
already in place. If you're running the Bitmask bundles, the first time you will
be prompted to authenticate to allow these helpers to be copied over (or any
time that these helpers change).

However, if you're running bitmask in a headless environment, you will want to
copy the helpers manually, without involving pkexec. To do that, use::

  sudo `which bitmask_helpers` install 

You can also uninstall them::

  sudo `which bitmask_helpers` uninstall 


.. note: split a Contributing page on its own, this is getting too long/messy

How to contribute code
---------------------------------

* Send your merge requests to https://0xacab/leap/bitmask-dev, it will be
  subject to code-review.
* Please base your branch for master, and keep it rebased when you push.
* After review, please squash your commits.
 

Coding conventions
---------------------------------

* Follow pep8 for all the python code.
* Git messages should be informative.
* There is a pre-commit hook ready to be used in the ``docs/hooks`` folder,
  alongside some other hooks to do autopep8 on each commit.

.. include:: ../hooks/leap-commit-template.README
   :literal:

Dependencies
----------------------------------

We try hard not to introduce any new dependencies at this moment. If you really
have to, the packages bitmask depends on have to be specified *both* in the
setup.py and the pip requirements file.

Don't introduce any pinning in the setup.py file, they should go in the
requirements files (mainly ``pkg/requirements.pip``).


Signing your commits
---------------------------------

For contributors with commit access, you **should** sign all your commits. If
you are merging some code from external contributors, you should sign their
commits.

For handy alias for sign and signoff commits from external contributors add to
your gitconfig::

  [alias]
  # Usage: git signoff-rebase [base-commit]
  signoff-rebase = "!GIT_SEQUENCE_EDITOR='sed -i -re s/^pick/e/' sh -c 'git rebase -i $1 && while test -f .git/rebase-merge/interactive; do git commit --amend --signoff --no-edit && git rebase --continue; done' -"

Merging code
---------------------------------

We avoid merge commits into master, they make a very messy history. Put this
in your gitconfig to only allow the merges that can be resolved as a
fast-forward::

  [merge]
  ff = only  


Making a new release
--------------------

A checklist for the release process can be found :ref:`here <release>`

As part of the release we also tag upload snapshots of the ``leap.bitmask_js``
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
* Minimal C++ Qt client (see `kali's bitmaskqt5 repo`_)

.. _`kali's bitmaskqt5 repo`: https://github.com/kalikaneko/bitmaskqt5
