import commands
import os

from behave import given, when, then
from common import (
    click_button,
    wait_until_button_is_visible,
)
from selenium.common.exceptions import TimeoutException
# For checking IP
import requests

resolv = None


def apply_dns_workaround():
    # we need this until we can get proper iptables execution
    # because of the dns rewrite hacks in the firewall
    print("CURRENT UID %s" % os.getuid())
    if os.getuid() == 0:
        global resolv
        resolv = commands.getoutput('cat /etc/resolv.conf')
        print("original resolv.conf: %s" % resolv)
        result = commands.getoutput(
            'echo "nameserver 10.41.0.1" > /etc/resolv.conf')
        resolv2 = commands.getoutput('cat /etc/resolv.conf')
        print("changed resolv.conf: %s" % resolv2)
        print("Workaround OK")


def deapply_dns_workaround():
    if os.getuid() == 0:
        commands.getoutput(
            'echo "nameserver 85.214.20.141" > /etc/resolv.conf')


@given('An initial network configuration')
def record_ip(context):
    context.initial_ip = _current_ip()


def _current_ip():
    url = 'https://ipapi.co/json'

    r = requests.get(url)
    try:
        data = r.json()
    except Exception:
        print("ERROR: data received was %s" % r.content)
        raise

    current_ip = data.get('ip')
    print("Current IP: %s\n\n" % current_ip)
    return current_ip


@when('I activate VPN')
def activate_vpn(context):
    try:
        click_button(context, 'Install Helper Files')
    except TimeoutException:
        pass
    click_button(context, 'Turn ON')


@then('I should have my ass covered')
def assert_vpn(context):
    wait_until_button_is_visible(context, 'Turn OFF')
    apply_dns_workaround()
    assert _current_ip() != context.initial_ip


@when('I deactivate VPN')
def deactivate_vpn(context):
    click_button(context, 'Turn OFF')
    wait_until_button_is_visible(context, 'Turn ON', timeout=60)


@then('My network should be configured as before')
def network_as_before(context):
    deapply_dns_workaround()
    ip = _current_ip()
    assert ip == context.initial_ip
