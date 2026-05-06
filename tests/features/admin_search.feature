Feature: Admin User Search
  As an Admin user
  I want to search for users by their role
  So that I can manage system users efficiently

Scenario Outline: Search users with different roles
    Given the user is on the OrangeHRM login page
    When the user logs in with "Admin" and "admin123"
    And the user navigates to the "Admin" section
    And the user searches for role "<role>"
    Then the "User Role" column in the first row should contain "<expected_username>"

    Examples:
      | role    | expected_username           |
      | Admin   | Admin                       |
      | ESS     | Alfredo_Manriquez@demo.com  |
   