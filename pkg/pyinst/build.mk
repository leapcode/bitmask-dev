# This makefile should be called from the topmost bitmask folder
#
bundle: bundle_clean
	pyinstaller -y pkg/pyinst/app.spec
	cp $(VIRTUAL_ENV)/lib/python2.7/site-packages/_scrypt.so $(DIST)
	cp src/leap/bitmask/core/bitmaskd.tac $(DIST)
	mkdir $(DIST)/leap
	# if you find yourself puzzled becase the following files are not found in your
	# virtualenv, make sure that you're installing the packages from wheels and not eggs.
	mkdir -p $(DIST)/leap/soledad/client/_db
	cp $(VIRTUAL_ENV)/lib/python2.7/site-packages/leap/soledad/client/_db/dbschema.sql $(DIST)/leap/soledad/client/_db/
	cp -r $(VIRTUAL_ENV)/lib/python2.7/site-packages/leap/bitmask_js  $(DIST)/leap/
	cp -r $(VIRTUAL_ENV)/lib/python2.7/site-packages/pixelated_www  $(DIST)/
	mv $(DIST) _bundlelib && mkdir $(DIST_VERSION) && mv _bundlelib $(DIST_VERSION)/lib/
	cd pkg/launcher && make
	cp pkg/launcher/bitmask $(DIST_VERSION)

bundle_win:
	pyinstaller -y pkg/pyinst/app.spec
	cp ${VIRTUAL_ENV}/Lib/site-packages/_scrypt.pyd $(DIST)
	cp ${VIRTUAL_ENV}/Lib/site-packages/zmq/libzmq.pyd $(DIST)
	cp src/leap/bitmask/core/bitmaskd.tac $(DIST)

bundle_linux_gpg:
	# TODO build it in a docker container!
	mkdir -p $(DIST_VERSION)/apps/mail
	cp /usr/bin/gpg $(DIST_VERSION)/apps/mail/
	# workaround for missing libreadline.so.6 in fresh ubuntu
	patchelf --set-rpath '.' $(DIST_VERSION)/apps/mail/gpg
	cp /lib/x86_64-linux-gnu/libusb-0.1.so.4 $(DIST_VERSION)/lib

bundle_linux_vpn:
	mkdir -p $(DIST_VERSION)/apps/vpn
	# TODO verify signature
	wget https://downloads.leap.se/thirdparty/linux/openvpn/openvpn -O $(DIST_VERSION)/apps/vpn/openvpn.leap

bundle_linux_helpers:
	mkdir -p $(DIST_VERSION)/apps/helpers
	cp src/leap/bitmask/vpn/helpers/linux/bitmask-root $(DIST_VERSION)/apps/helpers/
	cp src/leap/bitmask/vpn/helpers/linux/se.leap.bitmask.bundle.policy $(DIST_VERSION)/apps/helpers/

bundle_osx_helpers:
	mkdir -p $(DIST_VERSION)/apps/helpers
	cp src/leap/bitmask/vpn/helpers/osx/bitmask-helper $(DIST_VERSION)/apps/helpers/
	cp src/leap/bitmask/vpn/helpers/osx/bitmask.pf.conf $(DIST_VERSION)/apps/helpers/
	cp pkg/osx/se.leap.bitmask-helper.plist $(DIST_VERSION)/apps/helpers/
	cp -r pkg/osx/daemon $(DIST_VERSION)/apps/helpers/
	cp -r pkg/osx/openvpn $(DIST_VERSION)/apps/helpers/


bundle_apps_linux: bundle_linux_gpg bundle_linux_vpn bundle_linux_helpers

bundle_apps_osx: bundle_osx_helpers

bundle_tar:
	cd dist/ && tar cvzf Bitmask.$(NEXT_VERSION).tar.gz bitmask-$(NEXT_VERSION)

bundle_sign:
	gpg2 -a --sign --detach-sign dist/Bitmask.$(NEXT_VERSION).tar.gz 

bundle_upload:
	rsync --rsh='ssh' -avztlpog --progress --partial dist/Bitmask.$(NEXT_VERSION).* downloads.leap.se:./

bundle_clean:
	rm -rf "dist" "build"

