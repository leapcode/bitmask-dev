import commands
import os
import sys
import shutil
import re

from urlparse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from leap.common.config import get_path_prefix

DEFAULT_IMPLICIT_WAIT_TIMEOUT_IN_S = 60
HOME_PATH = os.path.abspath('./tmp/bitmask-test')

VIRTUALENV = 'virtualenv'
BUNDLE = 'bundle'
BUNDLE_CI = 'bundle-ci'

MODE = VIRTUALENV


def set_mode(mode):
    global MODE
    if mode not in (VIRTUALENV, BUNDLE, BUNDLE_CI):
        raise ValueError('Unknown test mode: %s' % mode)
    MODE = mode
    return mode


def before_all(context):
    os.environ['HOME'] = HOME_PATH
    mode = os.environ.get('TEST_MODE', 'virtualenv')
    set_mode(mode)
    context.mode = mode

    _setup_webdriver(context)
    userdata = context.config.userdata
    context.host = userdata.get('host', 'http://localhost')
    if not context.host.startswith('http'):
        context.host = 'https://{}'.format(context.host)
    context.hostname = urlparse(context.host).hostname

    try:
        context.username = os.environ['TEST_USERNAME']
        context.password = os.environ['TEST_PASSWORD']
        context.user_email = '{}@{}'.format(context.username, context.hostname)
    except KeyError:
        print('TEST_USERNAME or TEST_PASSWORD not set')
        sys.exit(0)

    if MODE == BUNDLE:
        next_version = open('pkg/next-version').read().strip()
        context.bundle_path = os.path.abspath(
            os.path.join('dist', 'bitmask-' + next_version))
    elif MODE == BUNDLE_CI:
        # TODO set path to artifact XXX ---
        context.bundle_path = None
    else:
        context.bundle_path = None


def _setup_webdriver(context):
    chrome_options = Options()
    # argument to switch off suid sandBox and no sandBox in Chrome
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")

    context.browser = webdriver.Chrome(chrome_options=chrome_options)
    context.browser.set_window_size(1280, 1024)
    context.browser.implicitly_wait(DEFAULT_IMPLICIT_WAIT_TIMEOUT_IN_S)
    context.browser.set_page_load_timeout(60)


def after_all(context):
    context.browser.quit()
    if MODE == VIRTUALENV:
        commands.getoutput('bitmaskctl stop')


def after_step(context, step):
    if step.status == 'failed':
        _prepare_artifacts_folder(step)
        _save_screenshot(context, step)
        _save_config(context, step)
        _debug_on_error(context, step)


def _prepare_artifacts_folder(step):
    try:
        os.makedirs(_artifact_path(step))
    except OSError as err:
        # directory existed
        if err.errno != 17:
            raise


def _save_screenshot(context, step):
    filepath = _artifact_path(step, 'screenshot.png')
    context.browser.save_screenshot(filepath)
    print('saved screenshot to: file://%s' % filepath)


def _save_config(context, step):
    filepath = _artifact_path(step, 'config')
    try:
        shutil.copytree(get_path_prefix(), filepath)
    except OSError:
        pass
    print('copied config folder to:    file://%s' % filepath)


def _artifact_path(step, filename=''):
    slug = re.sub('\W', '-', str(step.name))
    return os.path.abspath(os.path.join('failures', slug, filename))


def _debug_on_error(context, step):
    if context.config.userdata.getbool("debug"):
        try:
            import ipdb
            ipdb.post_mortem(step.exc_traceback)
        except ImportError:
            import pdb
            pdb.post_mortem(step.exc_traceback)
