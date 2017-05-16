#!/bin/bash

#############################################################################
# Builds OpenVPN statically against polarssl.
# Requirements:  cmake
#############################################################################

set -e
set -x

platform='unknown'
unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
   platform='linux'
elif [[ "$unamestr" == 'Darwin' ]]; then
   platform='osx'
fi

BUILDDIR="openvpn_build"
mkdir -p ~/$BUILDDIR && cd ~/$BUILDDIR

BASE=`pwd`
SRC=$BASE/src
mkdir -p $SRC

LZO="lzo-2.10"
ZLIB="zlib-1.2.11"
MBEDTLS="mbedtls-2.4.2"
OPENVPN="openvpn-2.4.1"

WGET="wget --prefer-family=IPv4"
DEST=$BASE/install
LDFLAGS="-L$DEST/lib -L$DEST/usr/local/lib -W"
CPPFLAGS="-I$DEST/include"
CFLAGS="-D_FORTIFY_SOURCE=2 -O1 -Wformat -Wformat-security -fstack-protector -pie -fPIE"
CXXFLAGS=$CFLAGS
CONFIGURE="./configure --prefix=/install"
MAKE="make -j2"


######## ####################################################################
# ZLIB # ####################################################################
######## ####################################################################

function build_zlib()
{
	mkdir $SRC/zlib && cd $SRC/zlib

	if [ ! -f $ZLIB.tar.gz ]; then
	    $WGET http://zlib.net/$ZLIB.tar.gz
	fi
	tar zxvf $ZLIB.tar.gz
	cd $ZLIB

	LDFLAGS=$LDFLAGS \
	CPPFLAGS=$CPPFLAGS \
	CFLAGS=$CFLAGS \
	CXXFLAGS=$CXXFLAGS \
	./configure \
	--prefix=/install

	$MAKE
	make install DESTDIR=$BASE
}

############ #################################################################
# POLARSSL # #################################################################
############ #################################################################

function build_mbedtls()
{
	mkdir -p $SRC/polarssl && cd $SRC/polarssl
	if [ ! -f $MBEDTLS-gpl.tgz ]; then
	    $WGET https://tls.mbed.org/download/$MBEDTLS-gpl.tgz
	fi
	tar zxvf $MBEDTLS-gpl.tgz
	cd $MBEDTLS
	mkdir -p build
	cd build
	cmake ..
	$MAKE
	make install DESTDIR=$BASE/install
}

######## ####################################################################
# LZO2 # ####################################################################
######## ####################################################################

function build_lzo2()
{
	mkdir $SRC/lzo2 && cd $SRC/lzo2
	if [ ! -f $LZO.tar.gz ]; then
	    $WGET http://www.oberhumer.com/opensource/lzo/download/$LZO.tar.gz
	fi
	tar zxvf $LZO.tar.gz
	cd $LZO

	LDFLAGS=$LDFLAGS \
	CPPFLAGS=$CPPFLAGS \
	CFLAGS=$CFLAGS \
	CXXFLAGS=$CXXFLAGS \
	$CONFIGURE --enable-static --disable-debug

	$MAKE
	make install DESTDIR=$BASE
}

########### #################################################################
# OPENVPN # #################################################################
########### #################################################################

function build_openvpn()
{
	mkdir $SRC/openvpn && cd $SRC/openvpn
	if [ ! -f $OPENVPN.tar.gz ]; then
	    $WGET http://swupdate.openvpn.org/community/releases/$OPENVPN.tar.gz
	fi
	tar zxvf $OPENVPN.tar.gz
	cd $OPENVPN

	POLARSSL_CFLAGS=-I$DEST/usr/local/include \
	POLARSSL_LIBS=$DEST/lib/ \
	LDFLAGS=$LDFLAGS \
	CPPFLAGS=$CPPFLAGS \
	CFLAGS=$CFLAGS \
	CXXFLAGS=$CXXFLAGS \
	$CONFIGURE \
	--disable-plugin-auth-pam \
	--enable-password-save \
	--with-crypto-library=mbedtls \
	--enable-small \
	--disable-debug

	$MAKE LIBS="-all-static -lssl -lcrypto -lz -llzo2"
	make install DESTDIR=$BASE/openvpn
}

function main()
{
    if [[ $platform == 'linux' ]]; then
        build_zlib
	build_mbedtls
	build_lzo2
	build_openvpn
    fi
}

main "$@"
