#!/bin/bash
#######################################
# Bootstrap a bitmask-dev environment #
#######################################

set -e

APT_DEPS="build-essential python-pip python-dev python-virtualenv libsqlcipher-dev libssl1.0-dev libffi-dev haveged python-pyqt5 python-pyqt5.qtwebkit gnupg1 openvpn"

function add_pew_to_environment()
{
  while true; do
    read -p "Do you want to add pew executable to your .zshrc?> " yn
    case $yn in
	    [Yy]* ) echo "PATH=~/.local/bin:\$PATH" >> ~/.zshrc; echo "source \$(pew shell_config)" >> ~/.zshrc; break;;
	    [Nn]* ) return;;
	    * ) echo "Please answer yes or no.";;
    esac
  done
}

function apt_install()
{
  sudo apt install $APT_DEPS
}

function init_pew()
{
  which pew || pip install pew
  which pew || add_pew_to_environment
  PATH=~/.local/bin:$PATH
  # this hangs when creating for the first time
  pew ls | grep bitmask || echo '[+] bitmask boostrap: creating new bitmask virtualenv. Type "exit" in the shell to continue!' && pew new bitmask
}

function clone_repo()
{
  mkdir -p ~/leap/ && cd ~/leap
  git clone https://0xacab.org/leap/bitmask-dev || echo 'not cloning: bitmask-dev already exists...'
}

function install_deps()
{
  cd ~/leap/bitmask-dev && pew in bitmask pip install -U -r pkg/requirements-dev.pip
  cd ~/leap/bitmask-dev && pew in bitmask pip install -U -r pkg/requirements-testing.pip
  cd ~/leap/bitmask-dev && pew in bitmask make dev-all
}

apt_install
init_pew
clone_repo
install_deps
pew workon bitmask
