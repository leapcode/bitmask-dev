:LastChangedDate: $LastChangedDate$
:LastChangedRevision: $LastChangedRevision$
:LastChangedBy: $LastChangedBy$

.. _install:


Installation and packaging 
==========================

Users: go to the Bitmask Install guide https://bitmask.net/en/install

Translators: improved/new translations welcome!


.. toctree::
   :hidden:

Running latest code
-------------------

Refer to the :ref:`setting up the development environment <devenv>` section to
learn how to run Bitmask from the latest code in the master branch.

Building new bundles
--------------------

The standalone bundles are built with PyInstaller.

If you are inside a development virtualenv, you should be able to install it
together with some extra development dependencies with::

  pip install -r pkg/requirements-dev.pip

And then just do::

  make bundle

To build a new bundle.

There's also a script that automates re-creating the virtualenv from which the
packaging takes place:: 
  
  pkg/build_bundle_with_venv.sh

To ensure a repeatable system-wide environment, you can build those bundles from
within a docker container. First you need to create the container::

  make docker_container

and then you can launch the above script inside that container::

  make bundle_in_docker

A new bundle is created by the CI for every commit using this procedure
involving docker, you can read more about the bundles in the :ref:`qa section
<qa>`.

Debian packages
---------------

ubuntu:
https://bitmask.net/en/install/linux#ubuntu-packages

debian:
https://bitmask.net/en/install/linux#debian-packages


Building latest packages (TBD).


Archlinux
---------

Not officially supported, but DoctorJellyFace maintains a PKGBUILD that can be found in the `AUR`_ repo.

.. _`AUR`: https://aur.archlinux.org/packages/bitmask_client/
