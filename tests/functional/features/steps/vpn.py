from behave import given, when, then
from common import (
    click_button,
    wait_until_button_is_visible,
    find_element_containing_text
)
from selenium.common.exceptions import TimeoutException
# For checking IP
import requests


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
    assert _current_ip() != context.initial_ip


@when('I deactivate VPN')
def deactivate_vpn(context):
    click_button(context, 'Turn OFF')
    wait_until_button_is_visible(context, 'Turn ON')


@then('My network should be configured as before')
def network_as_before(context):
    ip = _current_ip()
    assert ip == context.initial_ip
