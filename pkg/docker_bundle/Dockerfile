# This is *almost* a copy of the file that's used for building the bundle docker image.
# The copy that the CI uses is in tests/docker/Dockerfile

# It has diverged from the original, but it's because I don't want the clutter
# of all the nodejs and friends inside a container for bundling -- kali.

FROM ubuntu:17.10

MAINTAINER LEAP Encryption Access Project <info@leap.se>
LABEL Description="Image for building Bitmask bundle based on Ubuntu 17:04" Vendor="LEAP" Version="1.1"

RUN apt update && apt upgrade -y

# Install bitmask-dev build deps
RUN apt install -y --no-install-recommends \
  build-essential virtualenv libpython-dev \
  libsqlcipher-dev libssl-dev libffi-dev \
  python-pyqt5 python-pyqt5.qtwebengine \
  libusb-0.1-4 patchelf wget \
  git
