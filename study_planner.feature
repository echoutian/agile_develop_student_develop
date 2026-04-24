Feature: Study Planner Application - Sprint 1 & Sprint 2 User Stories
  # Tests are written against the exact acceptance criteria from the product backlog
  # and the provided Flask implementation (routes.py, models.py, forms.py, admin_recorator.py)

  # S1.1 - Task Input (Add Study Task)
  Scenario: S1.1 Add Study Task
    Given I am logged in as a student
    And I enter task name, type, and deadline
    When I save the task
    Then it appears in my task list

  # S1.2 - View Plan (View Study Plan)
  Scenario: S1.2 View Study Plan
    Given I am logged in as a student
    And a plan is generated
    When I open the plan page
    Then I see daily tasks in order

  # S1.3 - Task Editing (Edit/Delete Task)
  Scenario: S1.3 Edit/Delete Task
    Given I am logged in as a student
    And task exists
    When I edit or delete the task
    Then my task list stays accurate

  # S1.4 - Notifications (Reminders) - Nice-to-have (no implementation yet in routes, so test behaviour only)
  Scenario: S1.4 Reminders
    Given I am logged in as a student
    And deadline approaching
    When the reminder is triggered
    Then I receive a reminder so that I don’t miss deadlines

  # S2.1 - Community Forum (Create Forum Post)
  Scenario: S2.1 Create Forum Post
    Given I am logged in as a student
    And I enter a title and content
    When I click “Post”
    Then my post appears in the recent posts list

  # S2.2 - Community Forum (View Recent Posts)
  Scenario: S2.2 View Recent Posts
    Given I am logged in as a student
    And posts exist
    When I visit the forum page
    Then I see posts with author, timestamp, and preview

  # S2.3 - Mental Health Resources (Access Support Page)
  Scenario: S2.3 Access Support Page
    Given I am logged in as a student
    And I navigate to the health page
    When resources are available
    Then I see curated support links/information

  # S2.4 - Mental Health Resources (Admin Resource Management)
  Scenario: S2.4 Admin Resource Management
    Given I am logged in as admin
    And I edit resources
    When I save the changes
    Then changes are reflected on the student-facing page