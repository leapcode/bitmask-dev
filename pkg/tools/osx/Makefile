# this mimicks what is done by the installer
install_helper:
	sudo mkdir -p /Applications/RiseupVPN.app/Contents/Resources/bitmask-helper/
	sudo cp ../../osx/daemon/* /Applications/RiseupVPN.app/Contents/Resources/bitmask-helper/
	sudo cp ../../../src/leap/bitmask/vpn/helpers/osx/* /Applications/RiseupVPN.app/Contents/Resources/bitmask-helper/
	sudo cp ../../osx/scripts-riseupvpn/se.leap.bitmask-helper.plist /Library/LaunchDaemons/se.leap.bitmask-helper.plist
unload_helper:
	sudo launchctl unload /Library/LaunchDaemons/se.leap.bitmask-helper.plist
load_helper:
	sudo launchctl load /Library/LaunchDaemons/se.leap.bitmask-helper.plist
