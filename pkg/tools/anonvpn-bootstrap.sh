#!/bin/bash
#######################################
# Bootstrap an anonvpn environment    #
#######################################

set -e

APT_DEPS="build-essential python-pip python-dev python-virtualenv libssl-dev libffi-dev openvpn"

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
  pew ls | grep anonvpn || echo '[+] creating new anonvpn virtualenv...' && pew new -d anonvpn
}

function clone_repo()
{
  mkdir -p ~/leap/ && cd ~/leap
  git clone https://0xacab.org/leap/bitmask-dev || echo 'not cloning: bitmask-dev already exists...'
}

function install_deps()
{
  cd ~/leap/bitmask-dev && pew in anonvpn pip install -U -r pkg/requirements-dev.pip
  cd ~/leap/bitmask-dev && pew in anonvpn make dev-backend
}

apt_install
init_pew
clone_repo
install_deps
pew workon bitmask
