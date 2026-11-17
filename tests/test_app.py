import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

TEST_ACTIVITY = "Test Activity"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setitem(
        activities,
        TEST_ACTIVITY,
        {
            "description": "Activity used by API tests",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 10,
            "participants": [],
        },
    )

    with TestClient(app) as test_client:
        yield test_client


def test_get_activities_includes_activity(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()[TEST_ACTIVITY]["participants"] == []


def test_signup_adds_participant(client):
    email = "student@mergington.edu"

    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {TEST_ACTIVITY}"
    assert activities[TEST_ACTIVITY]["participants"] == [email]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    email = "student@mergington.edu"
    activities[TEST_ACTIVITY]["participants"].append(email)

    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[TEST_ACTIVITY]["participants"] == [email]


def test_unregister_removes_participant(client):
    email = "student@mergington.edu"
    activities[TEST_ACTIVITY]["participants"].append(email)

    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {TEST_ACTIVITY}"
    assert activities[TEST_ACTIVITY]["participants"] == []


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
