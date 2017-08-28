import commands
import shutil
import os
import time
from leap.common.config import get_path_prefix

from behave import given


@given('I start bitmask for the first time')
def initial_run(context):
    if context.mode == 'virtualenv':
        cmd = commands.getoutput('which bitmaskctl')
        # print("CMD PATH", cmd)
        commands.getoutput('bitmaskctl stop')
        # TODO: fix bitmaskctl to only exit once bitmaskd has stopped
        time.sleep(2)
        _initialize_home_path()
        commands.getoutput('bitmaskctl start')
        time.sleep(1)
    elif context.mode in ('bundle', 'bundle-ci'):
        commands.getoutput(context.bundle_path)
        time.sleep(2)
    tokenpath = os.path.join(get_path_prefix(), 'leap', 'authtoken')
    token = open(tokenpath).read().strip()
    context.login_url = "http://localhost:7070/#%s" % token


def _initialize_home_path():
    shutil.rmtree(get_path_prefix(), ignore_errors=True)
    os.makedirs(get_path_prefix())
