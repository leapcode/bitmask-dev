import commands
import shutil
import os
import time
from leap.common.config import get_path_prefix

from behave import given


@given('I start bitmask for the first time')
def initial_run(context):
    commands.getoutput('bitmaskctl stop')
    # TODO: fix bitmaskctl to only exit once bitmaskd has stopped
    time.sleep(2)
    _initialize_home_path()
    commands.getoutput('bitmaskctl start')
    tokenpath = os.path.join(get_path_prefix(), 'leap', 'authtoken')
    token = open(tokenpath).read().strip()
    context.login_url = "http://localhost:7070/#%s" % token


def _initialize_home_path():
    home_path = '/tmp/bitmask-test'
    os.environ['HOME'] = home_path
    shutil.rmtree(get_path_prefix(), ignore_errors=True)
    os.makedirs(get_path_prefix())
