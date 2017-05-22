# start with a fresh image (that comes from Ubuntu 16.04 at the moment).

FROM 0xacab.org:4567/leap/bitmask-dev:latest

MAINTAINER LEAP Encryption Access Project <info@leap.se>
LABEL Description="Image for building bitmask-dev based on Ubuntu 16:04" Vendor="LEAP" Version="1.0"

RUN apt-get update

# Install bitmask-dev build and test deps
RUN apt-get -y install build-essential python-virtualenv libpython-dev \
  libsqlcipher-dev libssl-dev libffi-dev python-pyqt5 python-pyqt5.qtwebkit \
  nodejs npm nodejs-legacy mocha \
  git swaks uuid-runtime \
  openvpn policykit-1 lxpolkit \
  wget patchelf libusb-0.1-4 \
  docker.io \
