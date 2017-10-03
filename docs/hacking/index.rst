:LastChangedDate: $LastChangedDate$ 
:LastChangedRevision: $LastChangedRevision$
:LastChangedBy: $LastChangedBy$

Hacking
========================================

So you want to hack on Bitmask?  Thanks, and welcome!

This document assumes a ``Linux`` environment.

There are also ongoing documents with notes for setting up an :ref:`OSX
<osx-dev>` and a :ref:`Windows <win-dev>` working environments too,
contribution is very much welcome on those docs!

Running tests
-------------

Tox is all you need::

  tox


Test when changes are made to common/soledad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are developing against a non-published branch of ``leap.common`` or
``leap.soledad``, run instead::

  tox -e py27-dev

This expects ``leap_common`` and ``soledad`` repos to be checked out in the
parent folder.

Gitlab-runner
~~~~~~~~~~~~~

For debugging issues related to how tests are run by the gitlab CI, you need to install:

* docker_ce from docker's repositories.
* gitlab-runner from `gitlab's repositories`_
  
.. _`gitlab's repositories`: https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh


Architecture
------------ 

There is a small :ref:`explanation of the bitmask components <architecture>`
that might be helpful to get you started
with the different moving parts of the Bitmask codebase.

User Interface
--------------

The :ref:`Javascript User Interface <uidev>` has its own guide for developers.

Setup
-----

Read how to :ref:`setup your python development environment <devenv>` to start coding in no time.

Debug
-----

A must-read for debugging the Bitmask Core daemon is the :ref:`manhole HowTo <manhole>`.

Privileges
----------

Bitmask VPN needs administrative privileges. For developing, you
need to be sure that you have :ref:`installed the privileged helpers
<privileges>` and that you keep them udpated.


Contributing
------------

There are some :ref:`guidelines for contributing code <contributing>` that you
might want to check if you are insterested in developing with Bitmask.


Release
-------

We keep a :ref:`checklist <release-checklist>` for the release process.


Ideas
-----

Want to help, but you don't know where to start? Come talk to us on irc or the
mailing list!

Some areas in which we always need contribution are:

* Localization of the client (talk to elijah).
* Multiplatform gitlab runners
* Windows and OSX packaging (talk to kali)
* Windows Firewall integration for VPN
* Migrating components to py3 (look for vshyba or kali).
* Minimal C++ Qt client (see `kali's bitmaskqt5 repo`_)

.. _`kali's bitmaskqt5 repo`: https://github.com/kalikaneko/bitmaskqt5
