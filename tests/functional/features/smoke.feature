Feature: login and logout

  @smoke
  Scenario: See user panel after login
    Given I start bitmask for the first time
    When  I login
    Then  I should see the user panel

  @smoke
  Scenario: Log in and log out
    Given I start bitmask for the first time
    When  I login
    And   I logout
    Then  I should see the second login page

  @smoke
  Scenario: Turn VPN on
    Given I start bitmask for the first time
    And   An initial network configuration
    When  I login
    And   I activate VPN
    Then  I should have my ass covered

  @wip
  Scenario: Turn VPN on and off
    Given I start bitmask for the first time
    And   An initial network configuration
    When  I login
    And   I activate VPN
    And   I deactivate VPN
    Then  My network should be configured as before
