from behave import given, when, then

from common import (
    click_button,
    fill_by_css_selector,
    find_element_by_css_selector
)


@when(u'I login')
def login_user(context):
    login_page(context)
    enter_credentials(context)
    click_button(context, 'Log In')


def login_page(context):
    context.browser.get(context.login_url)
    context.browser.refresh()


def enter_credentials(context):
    fill_by_css_selector(context, 'textarea[id="loginUsername"]',
                         context.username)
    fill_by_css_selector(context, 'input[id="loginPassword"]',
                         context.password)


@then(u'I should see the user panel')
def see_home_screen(context):
    find_element_by_css_selector(context, '.main-panel')


@then(u'I logout')
@when(u'I logout')
def click_logout(context):
    # TODO: Have identifiers for the "second" login screen
    click_button(context, 'Log Out')


@then(u'I should see the second login page')
def see_second_login_page(context):
    # TODO: Have unique identifiers for the second login page
    #       (that differentiates from user panel)
    find_element_by_css_selector(context, '#loginUsername')
