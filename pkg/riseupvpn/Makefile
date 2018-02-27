build: installers
	# for speeding up build, see https://tribaal.io/making-lxd-fly-on-ubuntu-as-well.html
	sudo snapcraft cleanbuild
install:
	sudo snap install riseup-vpn_*.snap --dangerous --classic
uninstall:
	sudo snap remove riseup-vpn
init-lxd:
	sudo lxd init
installers:
	./pack_installers
