Feature: login and logout

  Scenario: See user panel after login
    Given I start bitmask for the first time
    When I login
    Then I should see the user panel

  Scenario: Log in and log out
    Given I start bitmask for the first time
    When I login
    And I logout
    Then I should see the second login page

  @smoke
  Scenario: Use VPN
    Given I start bitmask for the first time
    When I login
    And I activate VPN
    Then I should have my ass covered
