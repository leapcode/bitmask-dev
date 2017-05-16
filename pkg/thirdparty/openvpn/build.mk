build_static_openvpn:
	pkg/thirdparty/openvpn/build_openvpn.sh
	strip ~/openvpn_build/openvpn/install/sbin/openvpn

upload_openvpn:
	rsync --rsh='ssh' -avztlpog --progress --partial ~/openvpn_build/openvpn/install/sbin/openvpn downloads.leap.se:./public/thirdparty/linux/openvpn/

download_openvpn:
	wget https://downloads.leap.se/thirdparty/linux/openvpn/openvpn

clean_openvpn_build:
	rm -rf ~/openvpn_build
