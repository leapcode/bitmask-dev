#
# npm builds for development mode
#

dev-build: build-clean make-init
	npm install
	npm run build

dev-install: dev-build
	pip install -e pydist

# installs a prebuilt python package from
# the magical pypi place in the sky.
# (see below for how this is generated).

dev-install-prebuilt:
	pip install -U leap.bitmask_js

#
# distribution builds
#
# This builds a python package that distributes the compiled assets, 
# for usage when you don't want to install nodejs.
#
# A developer/maintainer should use only these two targets:
#
# - "make python-package-local": 
#   	builds & installs the python package (from wheel).
#
# - "make python-package":
#       builds & uploads the python package to pypi, 


python-package: clean pydist-build pydist-upload

python-package-local: clean pydist-build
	pip install pydist/dist/*.whl


pydist-build: make-init
	http_proxy= /usr/bin/npm install
	http_proxy= /usr/bin/npm run build:production
	cd pydist && python setup.py bdist_wheel

pydist-upload:
	cd pydist && python setup.py sdist upload -r pypi

#
# clean up and set up
#

make-init:
	test -d pydist/leap/bitmask_js || mkdir -p pydist/leap/bitmask_js
	touch pydist/leap/bitmask_js/__init__.py

build-clean:
	rm -rf pydist/leap/bitmask_js
	rm -rf pydist/dist
	rm -rf pydist/build

clean: build-clean
	rm -rf node_modules

uninstall-python-package:
	pip uninstall leap.bitmask_js

#
# Testing
#

test:
	npm run test

# This makes make run test even thoug there's already a directory
# named "test"
.PHONY: test
