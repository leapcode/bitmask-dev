.. _win-dev:

Setting up a development environment in Windows™
================================================

This document gathers notes to setup a development environment inside a virtual
machine or a baremetal one. Tested with Windows 7 so far.

There is some work in progress, that was done initially by Paixu, for building
the windows installers from within several docker containers running linux (see
``pkg/windows/Readme.rst``.

* Install ``git``
* Install Microsoft Visual C++ Compiler for Python 2.7 https://aka.ms/vcpython27
* ``scrypt`` needs some hacks. me (kali) have a .whl laying around, I needed to
  drop several non-standard includes in the include path to allow compilation.
* I'm using PySide for windows, the wheel installs without problems. The compat
  hacks so far are not very terrible, although it's an afterthought since we
  moved to PyQt5 a while ago.
* There are some ugly looks in the ``bitmask_js`` ui that need to be fixed.

