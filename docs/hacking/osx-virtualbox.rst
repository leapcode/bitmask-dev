.. _osx-vms:

OSX Virtualization
============================================

If you have acess to a OSX machine, you can setup virtual machines for setting up a gitlab runner.

Base Image
----------

.. note: convert this to ansible script or similar.

* Install homebrew (via the curl | sh script).

Install basic packages::

  brew install gpg1 wget openssl cryptography python

* Modify $PATH (.bash_profile), source it or login again to activate the PATH.

* Add a symlink from gpg1 to ``/usr/bin/gpg``

Install tox for the tests::

  pip install tox

* Copy ssh keys to access this machine.

* TODO - install virtualbox guest extensions.


Gitlab runner (on host)
-----------------------

* install gitlab-runner for osx [link]
* install virtualbox in the host machine
* configure ``.gitlab-runner/config.toml``

Run::
  gitlab-runner run

Debug mode::
  gilab-runner --debug run


Virtualbox cheatsheet
---------------------

Some useful commands::

  # list
  VBoxManage list vms
  # only running
  VBoxManage list runningvms
  # start headless
  VBoxManage startvm yosemite --type headless
  # poweroff
  VBoxManage controlvm yosemite poweroff

gitlab-runner keeps a snapshot with the name 'Base State', so it seems this is
the one you have to be sure that you modify with all the software you need.
It seems to me that if you just delete the first 'Base State' snapshot in the
snapshot sequence, it take the most recent state (virtualbox does a merge).

This is how ``gitlab-runner`` accesses ssh::

  VBoxManage modifyvm yosemite-runner-deadbeef --natpf1 gustssh,tcp,127.0.0.1,99999,,22

