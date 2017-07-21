from behave import when, then
from common import (
    click_button,
    wait_until_button_is_visible,
    find_element_containing_text
)
from selenium.common.exceptions import TimeoutException


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
    assert find_element_containing_text(context, 'Turn OFF', 'button')
