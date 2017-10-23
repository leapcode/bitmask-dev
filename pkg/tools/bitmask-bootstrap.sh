#!/bin/bash
#######################################
# Bootstrap a bitmask-dev environment #
#######################################

set -e

APT_DEPS="build-essential python-pip python-dev python-virtualenv libsqlcipher-dev libssl-dev libffi-dev haveged python-pyqt5 python-pyqt5.qtwebkit gnupg1 openvpn"

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
  sudo pip install pew
}

function init_pew()
{
  pew ls | grep bitmask || echo '[+] creating new bitmask virtualenv...' && pew new -d bitmask
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
