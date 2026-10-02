import os
import pytest

from fastapi.testclient import TestClient

from app.database import Base
from app.database import engine

from app.main import app

os.environ["DEMO_MODE"] = "true"

os.environ[
    "DATABASE_URL"
] = "sqlite:///./test_fitbuddy.db"

os.environ[
    "ADMIN_KEY"
] = "test-admin"




@pytest.fixture(
    autouse=True
)
def reset_db():

    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )

    yield


@pytest.fixture
def client():

    with TestClient(app) as client:

        yield client