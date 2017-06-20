#!/bin/sh
# Bitmask Post-Instalation script
cp se.leap.bitmask-helper.plist /Library/LaunchDaemons/
launchctl load /Library/LaunchDaemons/se.leap.bitmask-helper.plist || echo "Already loaded, skipping..."
