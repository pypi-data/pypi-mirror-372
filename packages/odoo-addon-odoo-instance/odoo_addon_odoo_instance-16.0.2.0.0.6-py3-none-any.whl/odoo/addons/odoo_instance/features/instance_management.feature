Feature: Instance management

  Scenario: Create and delete an instance
    Given the user is on the Odoo Instance form view
    When the user fills in the form with valid data
    And the user clicks on the "Save" button
    Then a new instance should be created
    When the user clicks on the "Delete" button
    Then the instance should be deleted
