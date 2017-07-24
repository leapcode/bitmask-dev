#!/bin/bash
#######################################
# Bootstrap a bitmask-dev environment #
#######################################

set -e

APT_DEPS="build-essential python-dev python-virtualenv libsqlcipher-dev libssl1.0-dev libffi-dev python-pyqt5 python-pyqt5.qtwebkit"

function add_pew_to_environment()
{
  while true; do
    read -p "Do you want to add pew executable to your .zshrc?> " yn
    case $yn in
	    [Yy]* ) echo "PATH=~/.local/bin:\$PATH" >> ~/.zshrc; echo "source \$(pew shell_config)" >> ~/.zshrc; break;;
	    [Nn]* ) exit;;
	    * ) echo "Please answer yes or no.";;
    esac
  done
}

function init_pew()
{
  which pew || pip install pew
  which pew || add_pew_to_environment
  PATH=~/.local/bin:$PATH
  pew ls | grep bitmask || pew new bitmask
}

function apt_install()
{
  sudo apt install $APT_DEPS
}

function clone_repo()
{
  mkdir -p ~/leap/ && cd ~/leap
  git clone https://0xacab.org/leap/bitmask-dev || echo 'not cloning: bitmask-dev already exists...'
}

function install_deps()
{
  cd ~/leap/bitmask-dev && pew in bitmask pip install -r pkg/requirements-dev.pip
  cd ~/leap/bitmask-dev && pew in bitmask pip install -r pkg/requirements-testing.pip
  cd ~/leap/bitmask-dev && pew in bitmask make dev-all
}

init_pew
apt_install
clone_repo
install_deps
