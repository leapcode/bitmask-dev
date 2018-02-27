# Build a snap package for RiseupVPN.
# (c) LEAP Encryption Access Project, 2018
# We have to use classic confinement because it does not seem to be another way, at the moment,
# to use policykit.

build: helpers
	# for speeding up build, see https://tribaal.io/making-lxd-fly-on-ubuntu-as-well.html
	sudo snapcraft cleanbuild
helpers:
	./pack_installers
install:
	sudo snap install riseup-vpn_*.snap --dangerous --classic
uninstall:
	sudo snap remove riseup-vpn
deps:
	sudo apt install snapcraft lxd
init-lxd:
	sudo lxd init
