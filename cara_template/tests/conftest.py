# tests/conftest.py

import pytest
from core import create_app

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {}  # Remove PostgreSQL-specific pool options for SQLite
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()