import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from database import Base

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_and_teardown():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

def test_create_lead_success():
    response = client.post("/leads", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "company": "Test Co",
        "job_title": "Manager",
        "country": "India",
        "industry": "Technology",
        "company_size": 100,
        "source": "website",
        "campaign": "newsletter",
        "message": "Hello"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["lead"]["email"] == "testuser@example.com"
    assert data["lead"]["id"] is not None

def test_create_lead_duplicate_email():
    lead_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "company": "Test Co",
        "job_title": "Manager",
        "country": "India",
        "industry": "Technology",
        "company_size": 100,
        "source": "website",
        "campaign": "newsletter",
        "message": "Hello"
    }
    first_response = client.post("/leads", json=lead_data)
    assert first_response.status_code == 200

    second_response = client.post("/leads", json=lead_data)
    assert second_response.status_code == 409


def test_create_lead_invalid_email():
    response = client.post("/leads", json={
        "name": "Test User",
        "email": "not-a-valid-email",
        "company": "Test Co",
        "job_title": "Manager",
        "country": "India",
        "industry": "Technology",
        "company_size": 100,
        "source": "website",
        "campaign": "newsletter",
        "message": "Hello"
    })
    assert response.status_code == 422


def test_score_high_tier_lead():
    create_response = client.post("/leads", json={
        "name": "VP Lead",
        "email": "vplead@example.com",
        "company": "Big Corp",
        "job_title": "VP of Sales",
        "country": "United States",
        "industry": "SaaS",
        "company_size": 500,
        "source": "demo_request",
        "campaign": "high_intent",
        "message": "Need this now"
    })
    lead_id = create_response.json()["lead"]["id"]

    score_response = client.post(f"/leads/{lead_id}/score")
    assert score_response.status_code == 200
    data = score_response.json()
    assert data["tier"] == "high"
    assert data["score"] == 70


def test_route_without_score_fails():
    create_response = client.post("/leads", json={
        "name": "Unscored Lead",
        "email": "unscored@example.com",
        "company": "Some Co",
        "job_title": "Analyst",
        "country": "India",
        "industry": "Finance",
        "company_size": 50,
        "source": "website",
        "campaign": "newsletter",
        "message": "Hi"
    })
    lead_id = create_response.json()["lead"]["id"]

    route_response = client.post(f"/leads/{lead_id}/route")
    assert route_response.status_code == 400


def test_approve_followup_without_draft_fails():
    create_response = client.post("/leads", json={
        "name": "No Draft Lead",
        "email": "nodraft@example.com",
        "company": "Some Co",
        "job_title": "Analyst",
        "country": "India",
        "industry": "Finance",
        "company_size": 50,
        "source": "website",
        "campaign": "newsletter",
        "message": "Hi"
    })
    lead_id = create_response.json()["lead"]["id"]

    approve_response = client.post(f"/leads/{lead_id}/approve-followup")
    assert approve_response.status_code == 400