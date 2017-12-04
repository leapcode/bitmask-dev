#!/bin/sh
HELPER_PLIST="/Library/LaunchDaemons/se.leap.bitmask-helper.plist"
sudo launchctl unload $HELPER_PLIST
sudo rm -rf /Applications/Bitmask.app
sudo rm -rf ~/Library/Preferences/leap
sudo rm $HELPER_PLIST
echo "Bitmask has been uninstalled from your system!"
