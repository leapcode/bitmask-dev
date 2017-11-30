#!/bin/sh
sudo launchctl unload /Library/LaunchDaemons/se.leap.bitmask-helper.plist
sudo rm -rf /Applications/Bitmask.app
sudo rm -rf ~/Library/Preferences/leap
echo "Bitmask has been uninstalled from your system!"
