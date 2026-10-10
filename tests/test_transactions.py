import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# A temporary in-memory database, so tests never touch your real data
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def sample(**changes):
    data = {
        "amount": 42.5,
        "merchant": "Swiggy",
        "category": "food",
        "date": "2026-10-03",
    }
    data.update(changes)
    return data


def test_create_transaction(client):
    r = client.post("/transactions", json=sample())
    assert r.status_code == 201
    assert r.json()["id"] == 1
    assert r.json()["merchant"] == "Swiggy"


def test_rejects_negative_amount(client):
    r = client.post("/transactions", json=sample(amount=-5))
    assert r.status_code == 422


def test_rejects_future_date(client):
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    r = client.post("/transactions", json=sample(date=tomorrow))
    assert r.status_code == 422


def test_filter_by_category(client):
    client.post("/transactions", json=sample(category="food"))
    client.post("/transactions", json=sample(category="travel"))
    r = client.get("/transactions", params={"category": "travel"})
    assert len(r.json()) == 1
    assert r.json()[0]["category"] == "travel"


def test_filter_by_date_range(client):
    client.post("/transactions", json=sample(date="2026-09-01"))
    client.post("/transactions", json=sample(date="2026-10-03"))
    r = client.get("/transactions", params={"start_date": "2026-10-01"})
    assert len(r.json()) == 1