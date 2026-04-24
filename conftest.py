import pytest
from app import app as flask_app
from app import db
from app.models import User

@pytest.fixture(scope="session")
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    })
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture(autouse=True)
def db_reset(app):
    with app.app_context():

        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def student_user(app):
    with app.app_context():
        user = User(username="student1", email="student@test.com")
        user.set_password("password")

        user.role = 'normal'
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(username="admin1", email="admin@test.com")
        user.set_password("password")
        user.role = 'admin'
        db.session.add(user)
        db.session.commit()
        return user