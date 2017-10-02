:LastChangedDate: $LastChangedDate$
:LastChangedRevision: $LastChangedRevision$
:LastChangedBy: $LastChangedBy$

.. _install:


Installation
============

Here you can find instructions for developers and advanced users. For **user
instructions**, you should refer to the official `Bitmask Install Guide`_. You
should only need to read the following sections if:

* You plan to contribute code to bitmask core libraries.
* You intend to develop the Bitmask JS User Interface.
* You are a prospective maintainer for some platform yet unsupported.
* Your platform is unsupported by the official packages, and you want to
  install the python packages in your system.

If you want to contribute translations to some of these sections, please get in
touch with us, it will be greatly appreciated to extend the community.

.. _`Bitmask Install Guide`: https://bitmask.net/en/install

.. _pip:

With Pip
--------

If we still do not provide packages for your platform (debian/ubuntu only at the moment), and for some reason you cannot run the bundles we offer for download, you still should be able to run bitmask downloading the packages from pypi. First you will need some dependencies in your system, that very probably will be provided by your package manager::

  lxpolkit openvpn gnupg1 python-pyside python-dev

Now you can install the latest bitmask package from pypi::

  pip install leap.bitmask[gui]

If you want also to use the pixelated MUA, you need to install an additional extra::

  pip install leap.bitmask[pixelated]


From git
--------

If you want to run latest code from git, you can refer to the :ref:`setting up
the development environment <devenv>` section to learn how to run Bitmask from
the latest code in the master branch.

Building bundles
----------------

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

Debian & ubuntu 
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
