import os
import re
import time
from urlparse import urlparse
import commands

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DEFAULT_IMPLICIT_WAIT_TIMEOUT_IN_S = 10


def before_all(context):
    _setup_webdriver(context)
    userdata = context.config.userdata
    context.host = userdata.get('host', 'http://localhost')
    if not context.host.startswith('http'):
        context.host = 'https://{}'.format(context.host)
    context.hostname = urlparse(context.host).hostname

    context.username = os.environ['TEST_USERNAME']
    context.password = os.environ['TEST_PASSWORD']
    context.user_email = '{}@{}'.format(context.username, context.hostname)


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
    commands.getoutput('bitmaskctl stop')


def after_step(context, step):
    if step.status == 'failed':
        _save_screenshot(context, step)
        _debug_on_error(context, step)


def _debug_on_error(context, step):
    if context.config.userdata.getbool("debug"):
        try:
            import ipdb
            ipdb.post_mortem(step.exc_traceback)
        except ImportError:
            import pdb
            pdb.post_mortem(step.exc_traceback)


def _save_screenshot(context, step):
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    filename = _slugify('{} failed {}'.format(timestamp, str(step.name)))
    filepath = os.path.join('/tmp/', filename + '.png')
    context.browser.save_screenshot(filepath)


def _slugify(string_):
    return re.sub('\W', '-', string_)
