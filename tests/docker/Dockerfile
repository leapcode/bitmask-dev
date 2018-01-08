FROM 0xacab.org:4567/leap/docker/ubuntu:artful_amd64

LABEL Description="Image for building bitmask-dev based on Ubuntu 17:10" Vendor="LEAP" Version="1.0"
MAINTAINER LEAP Encryption Access Project <info@leap.se>

# Install bitmask-dev build and test deps
RUN apt-get update && \
  apt-get -y install --no-install-recommends \
  build-essential python-virtualenv libpython-dev \
  libsqlcipher-dev libssl-dev libffi-dev \
  python-pyqt5 python-pyqt5.qtwebengine \
  libusb-0.1-4 patchelf wget \
  git \
  tox \
  nodejs npm mocha \
  swaks uuid-runtime \
  openvpn policykit-1 lxpolkit \
  xvfb gnupg1 haveged \
  # needed for chromedriver
  libgconf-2-4 chromium-browser unzip

WORKDIR /tmp
RUN wget https://chromedriver.storage.googleapis.com/2.33/chromedriver_linux64.zip && \
  unzip chromedriver_linux64.zip && \
  cp chromedriver /usr/local/bin

RUN /usr/local/bin/chromedriver --version
