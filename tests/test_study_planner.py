import pytest
from pytest_bdd import given, when, then, scenario
import sqlalchemy as sa
from app import db
from app.models import StudyPlan, StudyTask, Post, HealthResource


@scenario("study_planner.feature", "S1.1 Add Study Task")
def test_s11(): pass

@scenario("study_planner.feature", "S1.2 View Study Plan")
def test_s12(): pass

@scenario("study_planner.feature", "S1.3 Edit/Delete Task")
def test_s13(): pass

@scenario("study_planner.feature", "S1.4 Reminders")
def test_s14(): pass

@scenario("study_planner.feature", "S2.1 Create Forum Post")
def test_s21(): pass

@scenario("study_planner.feature", "S2.2 View Recent Posts")
def test_s22(): pass

@scenario("study_planner.feature", "S2.3 Access Support Page")
def test_s23(): pass

@scenario("study_planner.feature", "S2.4 Admin Resource Management")
def test_s24(): pass


@given("I am logged in as a student")
def login_as_student(client, student_user, app):
    with app.app_context():
        user = db.session.merge(student_user)
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)

@given("I am logged in as admin")
def login_as_admin(client, admin_user, app):
    with app.app_context():
        user = db.session.merge(admin_user)
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)

# S1.1
@given("I enter task name, type, and deadline")
def enter_task_details(): pass

@when("I save the task")
def save_task(client):

    client.post("/plan/create", data={
        "title": "Test Plan",
        "deadline": "2026-05-01",
        "task_titles[]": ["Math"],
        "task_hours[]": ["3.0"],
        "task_types[]": ["1"]
    }, follow_redirects=True)

@then("it appears in my task list")
def task_appears(app, student_user):
    with app.app_context():
        user = db.session.merge(student_user)
        plan = db.session.scalar(sa.select(StudyPlan).where(StudyPlan.student_id == user.id))
        assert plan is not None
        assert plan.title == "Test Plan"

# S1.2
@given("a plan is generated")
def plan_generated(client):
    save_task(client)

@when("I open the plan page")
def open_plan_page(client):
    assert client.get("/", follow_redirects=True).status_code == 200

@then("I see daily tasks in order")
def see_tasks_in_order(): pass

# S1.3
@given("task exists")
def task_exists(client):
    save_task(client)

@when("I edit or delete the task")
def edit_or_delete_task(client, app, student_user):
    with app.app_context():
        user = db.session.merge(student_user)
        task = db.session.scalar(sa.select(StudyTask).join(StudyPlan).where(StudyPlan.student_id == user.id))

        client.post(f"/task/{task.id}/edit", data={
            "title": "Updated",
            "estimated_hours": 4.0,
            "task_type": 1
        })

@then("my task list stays accurate")
def task_list_accurate(): pass

# S1.4 Reminders
@given("deadline approaching")
def deadline_approaching(): pass

@when("the reminder is triggered")
def trigger_reminder(): pass

@then("I receive a reminder so that I don’t miss deadlines")
def reminder_received(): pass

# S2.1
@given("I enter a title and content")
def enter_post_details(): pass

@when('I click “Post”')
def click_post(client):
    client.post("/forum", data={"title": "Test", "body": "Content"}, follow_redirects=True)

@then("my post appears in the recent posts list")
def post_appears(app):
    with app.app_context():
        assert db.session.scalar(sa.select(sa.func.count(Post.id))) > 0

# S2.2
@given("posts exist")
def posts_exist(client):
    client.post("/forum", data={"title": "Existing", "body": "Body"}, follow_redirects=True)

@when("I visit the forum page")
def visit_forum(client):
    assert client.get("/forum").status_code == 200

@then("I see posts with author, timestamp, and preview")
def see_posts_with_metadata(): pass

# S2.3
@given("I navigate to the health page")
def navigate_health(client):
    assert client.get("/health").status_code == 200

@when("resources are available")
def resources_available(app, admin_user):
    with app.app_context():
        admin = db.session.merge(admin_user)
        db.session.add(HealthResource(title="Tips", content="...", category="stress", admin_id=admin.id))
        db.session.commit()

@then("I see curated support links/information")
def see_resources(client):
    assert client.get("/health").status_code == 200

# S2.4
@given("I edit resources")
def edit_resources(client, app, admin_user):
    with app.app_context():
        admin = db.session.merge(admin_user)
        res = HealthResource(title="Old", content="...", category="old", admin_id=admin.id)
        db.session.add(res)
        db.session.commit()

    client.post("/health/create", data={
        "title": "New",
        "content": "Content",
        "category": "wellbeing"
    })

@when("I save the changes")
def save_changes(client): pass

@then("changes are reflected on the student-facing page")
def changes_reflected(client):
    assert client.get("/health").status_code == 200