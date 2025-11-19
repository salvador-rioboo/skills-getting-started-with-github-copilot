import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Make a deep copy of the original activities to restore after each test
    import copy
    original = {
        name: {**details, "participants": list(details["participants"])}
        for name, details in activities.items()
    }
    yield
    activities.clear()
    activities.update({name: {**details, "participants": list(details["participants"])} for name, details in original.items()})


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test.user@example.com"

    # Ensure not already signed up
    assert email not in activities[activity]["participants"]

    # Signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]

    # Signing up again should fail
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400

    # Unregister
    resp3 = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp3.status_code == 200
    assert resp3.json()["message"] == f"Unregistered {email} from {activity}"
    assert email not in activities[activity]["participants"]

    # Unregistering again should fail
    resp4 = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp4.status_code == 400
