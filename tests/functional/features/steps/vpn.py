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
    url = 'https://wtfismyip.com/json'

    r = requests.get(url)
    data = r.json()

    current_ip = data['YourFuckingIPAddress']
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
