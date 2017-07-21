DIST=dist/bitmask
NEXT_VERSION = $(shell cat pkg/next-version)
DIST_VERSION = dist/bitmask-$(NEXT_VERSION)/
include pkg/bundles/build.mk
include pkg/thirdparty/openvpn/build.mk

dev-bootstrap:
	pkg/tools/bitmask-bootstrap.sh

dev-mail:
	pip install -e '.[mail]'

dev-gui: install_pixelated
	pip install -e '.[gui]'
dev-backend:
	pip install -e '.[backend]'

dev-latest-backend: dev-backend
	pip install -e 'git+https://0xacab.org/leap/leap_pycommon@master#egg=leap.common'
	pip install -e 'git+https://0xacab.org/leap/soledad@master#egg=leap.soledad'

dev-all: install_pixelated
	pip install -I --install-option="--bundled" pysqlcipher
	pip install -e '.[all]'

dev-latest-all: dev-all
	pip install -e 'git+https://0xacab.org/leap/leap_pycommon@master#egg=leap.common'
	pip install -e 'git+https://0xacab.org/leap/soledad@master#egg=leap.soledad'

uninstall:
	pip uninstall leap.bitmask

test:
	tox

test_e2e:
	tests/e2e/e2e-test-mail.sh
	tests/e2e/e2e-test-vpn.sh

test_functional_setup:
	pip install behave selenium

test_functional:
	xvfb-run --server-args="-screen 0 1280x1024x24" behave --tags ~@wip --tags @smoke tests/functional/features -k --no-capture -D host=localhost

test_functional_graphical:
	behave --tags ~@wip --tags @smoke tests/functional/features -k --no-capture -D host=localhost

test_functional_graphical_wip:
	behave --tags @wip tests/functional/features -k --no-capture -D host=localhost

install_helpers:
	cp src/leap/bitmask/vpn/helpers/linux/bitmask-root /usr/local/sbin/
	cp src/leap/bitmask/vpn/helpers/linux/se.leap.bitmask.policy /usr/share/polkit-1/actions/

install_pixelated:
	pip install leap.pixelated leap.pixelated-www

qt-resources:
	pyrcc5 pkg/branding/icons.qrc -o src/leap/bitmask/gui/app_rc.py

doc:
	cd docs && make html

bundle_in_virtualenv:
	pkg/build_bundle_with_venv.sh

bundle_in_docker:
	# needs a docker container called 'mybundle', created with 'make docker_container'
	cat pkg/docker_build | docker run -i -v ~/leap/bitmask-dev:/dist -w /dist -u `id -u` mybundle bash

docker_container:
	cd pkg/docker_bundle && docker build -t mybundle .

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
