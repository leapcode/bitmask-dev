#!/bin/bash

#############################################################################
# Builds OpenVPN statically against mbedtls (aka polarssl).
# Requirements:  cmake
# Output: ~/openvpn_build/sbin/openvpn-x.y.z
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
MBEDTLS="mbedtls-2.6.0"
OPENVPN="openvpn-2.4.4"

# [!] This needs to be updated for every release --------------------------
LZO_SHA1="4924676a9bae5db58ef129dc1cebce3baa3c4b5d"
MBEDTLS_SHA1="0e657805b5dc9777e0e0333a95d7886ae8f0314e"
# -------------------------------------------------------------------------
ZLIB_KEYS="https://pgp.mit.edu/pks/lookup?op=get&search=0x783FCD8E58BCAFBA"
OPENVPN_KEYS="https://swupdate.openvpn.net/community/keys/security.key.asc"

WGET="wget --prefer-family=IPv4"
DEST=$BASE/install
LDFLAGS="-L$DEST/lib -L$DEST/usr/local/lib -W"
CPPFLAGS="-I$DEST/include"
CFLAGS="-D_FORTIFY_SOURCE=2 -O1 -Wformat -Wformat-security -fstack-protector -fPIE"
CXXFLAGS=$CFLAGS
CONFIGURE="./configure --prefix=/install"
MAKE="make -j2"


######## ####################################################################
# ZLIB # ####################################################################
######## ####################################################################

function build_zlib()
{
        gpg --fetch-keys $ZLIB_KEYS
	mkdir $SRC/zlib && cd $SRC/zlib

	if [ ! -f $ZLIB.tar.gz ]; then
	    $WGET https://zlib.net/$ZLIB.tar.gz
	    $WGET https://zlib.net/$ZLIB.tar.gz.asc
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
	sha1=`sha1sum $MBEDTLS-gpl.tgz | cut -d' ' -f 1`
	if [ "${MBEDTLS_SHA1}" = "${sha1}" ]; then
	    echo "[+] sha1 verified ok"
	else
	    echo "[!] problem with sha1 verification"
	    exit 1
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
	sha1=`sha1sum $LZO.tar.gz | cut -d' ' -f 1`
	if [ "${LZO_SHA1}" = "${sha1}" ]; then
	    echo "[+] sha1 verified ok"
	else
	    echo "[!] problem with sha1 verification"
	    exit 1
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
	gpg --fetch-keys $OPENVPN_KEYS
	if [ ! -f $OPENVPN.tar.gz ]; then
	    $WGET http://swupdate.openvpn.org/community/releases/$OPENVPN.tar.gz
	    $WGET http://swupdate.openvpn.org/community/releases/$OPENVPN.tar.gz.asc
	fi
	gpg --verify $OPENVPN.tar.gz.asc && echo "[+] gpg verification ok"
	tar zxvf $OPENVPN.tar.gz
	cd $OPENVPN

	MBEDTLS_CFLAGS=-I$BASE/install/usr/local/include/ \
	MBEDTLS_LIBS="$DEST/usr/local/lib/libmbedtls.a $DEST/usr/local/lib/libmbedcrypto.a $DEST/usr/local/lib/libmbedx509.a" \
	LDFLAGS=$LDFLAGS \
	CPPFLAGS=$CPPFLAGS \
	CFLAGS="$CFLAGS -I$BASE/install/usr/local/include" \
	CXXFLAGS=$CXXFLAGS \
	$CONFIGURE \
	--disable-plugin-auth-pam \
	--with-crypto-library=mbedtls \
	--enable-small \
	--disable-debug \
	--enable-iproute2

	$MAKE LIBS="-all-static -lz -llzo2"
	make install DESTDIR=$BASE/openvpn
	mkdir $BASE/sbin/
	cp $BASE/openvpn/install/sbin/openvpn $BASE/sbin/$OPENVPN
	strip $BASE/sbin/$OPENVPN
}

function build_all()
{
	build_zlib
	build_lzo2
	build_mbedtls
	build_openvpn
}

function main()
{
    if [[ $platform == 'linux' ]]; then
      build_all
    fi
    if [[ $platform == 'osx' ]]; then
      build_all
    fi
}

main "$@"
