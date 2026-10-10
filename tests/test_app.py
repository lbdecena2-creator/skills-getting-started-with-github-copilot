from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(
        {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
            },
            "Programming Class": {
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
            },
            "Gym Class": {
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30,
                "participants": ["john@mergington.edu", "olivia@mergington.edu"],
            },
        }
    )
    yield
    app_module.activities.clear()
    app_module.activities.update(original)


def test_duplicate_signup_is_rejected():
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_activity_cannot_overfill():
    activity = app_module.activities["Chess Club"]
    activity["participants"] = [f"student{i}@mergington.edu" for i in range(activity["max_participants"])]

    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )

    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


def test_participant_can_unregister():
    response = client.delete(
        "/activities/Chess Club/signup?email=MICHAEL%40mergington.edu"
    )

    assert response.status_code == 200
    assert app_module.activities["Chess Club"]["participants"] == [
        "daniel@mergington.edu"
    ]


def test_unregister_rejects_unknown_participant():
    response = client.delete(
        "/activities/Chess Club/signup?email=unknown%40mergington.edu"
    )

    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()


def test_unregister_rejects_unknown_activity():
    response = client.delete(
        "/activities/Unknown%20Club/signup?email=student%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_activities_refresh_after_signup_without_cache():
    signup_response = client.post(
        "/activities/Chess Club/signup?email=newstudent%40mergington.edu"
    )
    activities_response = client.get("/activities")

    assert signup_response.status_code == 200
    assert activities_response.status_code == 200
    assert activities_response.headers["cache-control"] == "no-store"
    assert "newstudent@mergington.edu" in activities_response.json()["Chess Club"]["participants"]
