FROM python:2.7-slim-stretch
MAINTAINER kali <kali@leap.se>

LABEL Description="Image for building Bitmask bundle based on python:2.7-slim-stretch" Vendor="LEAP" Version="1.0"

RUN apt update && apt upgrade -y
RUN pip install -U pip

# Install bitmask-dev build deps,
# plus some dependencies needed by bitmask-systray too,
# so that we can reuse the bundler image.
RUN apt install -y --no-install-recommends \
  build-essential virtualenv libpython-dev \
  libsqlcipher-dev libssl-dev libffi-dev \
  libsqlite3-dev libzmq3-dev \
  python-pyqt5 python-pyqt5.qtwebkit \
  libqt5printsupport5 \
  qttranslations5-l10n libgl1-mesa-glx \
  libusb-0.1-4 patchelf wget \
  gnupg1 git libgl1-mesa-glx \
  libappindicator3-dev libgtk-3-dev golang \
  libsodium-dev

# Pyinstaller custom versions
#ARG PYINSTALLER_TAG=v3.2
ARG PYINSTALLER_TAG=pyqt5_fix
#
# TODO 
# change to pyinstaller repo when pyqt5_fix is merged
#
#RUN git clone --depth 1 --single-branch --branch $PYINSTALLER_TAG https://github.com/pyinstaller/pyinstaller.git /tmp/pyinstaller
RUN git clone --depth 1 --single-branch --branch $PYINSTALLER_TAG https://github.com/bjones1/pyinstaller.git /tmp/pyinstaller
RUN cd /tmp/pyinstaller && pip install --force-reinstall .


# Get Bitmask code --------------------------------------------
RUN mkdir -p /src/leap
WORKDIR /src/leap

#ARG BITMASK_BRANCH=master
#ARG BITMASK_REPO=https://0xacab.org/leap/bitmask-dev
ARG BITMASK_BRANCH=feat/webkit-fallback
ARG BITMASK_REPO=https://0xacab.org/kali/bitmask-dev
#RUN git clone https://0xacab.org/leap/bitmask-dev
RUN git clone --depth 1 --single-branch --branch $BITMASK_BRANCH $BITMASK_REPO

WORKDIR /src/leap/bitmask-dev
RUN pip install pysqlcipher --install-option="--bundled"
RUN pip install leap.bitmask_js
RUN pip install -r pkg/requirements.pip

RUN pip install ".[mail]"
RUN make install_pixelated

# TODO -- build on different containers and orchestrate them
# build gnupg and openvpn binaries --------------------------
# RUN cd pkg/thirdparty/gnupg && ./build_gnupg.sh
# RUN cd pkg/thirdparty/openvpn && ./build_openvpn.sh
# -----------------------------------------------------------


# Some hacks to make dist-packages visible from the pip installation path in /usr/local
RUN ln -s /usr/lib/python2.7/dist-packages/PyQt5/ /usr/local/lib/python2.7/site-packages/PyQt5
RUN cd /usr/local/lib/python2.7/site-packages/PyQt5 && ln -s QtCore.x86_64-linux-gnu.so QtCore.so
RUN cd /usr/local/lib/python2.7/site-packages/PyQt5 && ln -s QtGui.x86_64-linux-gnu.so QtGui.so
RUN cd /usr/local/lib/python2.7/site-packages/PyQt5 && ln -s QtWidgets.x86_64-linux-gnu.so QtWidgets.so
RUN cd /usr/local/lib/python2.7/site-packages/PyQt5 && ln -s QtWebKit.x86_64-linux-gnu.so QtWebKit.so
RUN cd /usr/local/lib/python2.7/site-packages/PyQt5 && ln -s QtWebKitWidgets.x86_64-linux-gnu.so QtWebKitWidgets.so
RUN cd /usr/local/lib/python2.7/site-packages/PyQt5 && ln -s QtNetwork.x86_64-linux-gnu.so QtNetwork.so
RUN cd /usr/local/lib/python2.7/site-packages/PyQt5 && ln -s QtPrintSupport.x86_64-linux-gnu.so QtPrintSupport.so
RUN ln -s /usr/lib/python2.7/dist-packages/sip.x86_64-linux-gnu.so /usr/local/lib/python2.7/site-packages/sip.so
RUN ln -s /usr/lib/python2.7/dist-packages/sipconfig.py /usr/local/lib/python2.7/site-packages/
RUN ln -s /usr/lib/python2.7/dist-packages/sipconfig_nd.py /usr/local/lib/python2.7/site-packages/
RUN ln -s /usr/lib/python2.7/dist-packages/sip.pyi /usr/local/lib/python2.7/site-packages/

# get dependencies for bitmask-systray so that builds are quick
RUN export GOPATH=/srv/go &&  \
   export CGO_CPPFLAGS="-I/usr/include" && \
   export CGO_LDFLAGS="-L/usr/lib -L/usr/lib/z86_64-linux-gnu -lzmq -lpthread -lsodium -lrt -lstdc++ -lm -lc -lgcc" && \
   go get 0xacab.org/leap/bitmask-systray
