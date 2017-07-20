# Bitmask functional UI tests

## Todo

Moved to https://0xacab.org/leap/bitmask-dev/issues/8929#note_111673

## Setup

Ubuntu:

    sudo apt install xvfb chromium-chromedriver
    ln -s /usr/lib/chromium-browser/chromedriver venv-all/bin/chromedriver

Debian:

    sudo apt install xvfb chromedriver


Setup your virtualenv and python packages:

    virtualenv venv-all
    source ./venv-all/bin/activate
    make dev-all
    make test_functional_setup

## Run tests

    source ./venv-all/bin/activate
    export TEST_USERNAME='user@provider.tld' TEST_PASSWORD='...'
    make test_functional

# Develop tests

When tests are run using `make test_functional` no window shows you what the browser sees.
In order to see tests running in the browser run:

    make test_functional_graphical

You can also run behave by itself and have a browser window to watch, i.e. to run all tests tagged as `@wip`:

    behave --wip -k -D host=localhost tests/functional/features
