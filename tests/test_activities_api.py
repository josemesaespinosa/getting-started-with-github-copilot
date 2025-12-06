from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants lists so tests can mutate without affecting other tests
    original = {k: v["participants"][:] for k, v in activities.items()}
    yield
    # restore
    for k, v in original.items():
        activities[k]["participants"] = v[:]


def test_get_activities_returns_200():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)


def test_signup_and_prevent_duplicate():
    client = TestClient(app)
    activity = "Chess Club"
    email = "tester@example.com"

    # signup should succeed
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # signing up again should fail with 400
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400


def test_unregister_participant():
    client = TestClient(app)
    activity = "Programming Class"
    email = "unregister-me@example.com"

    # add participant first
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # now remove
    resp2 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp2.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    client = TestClient(app)
    activity = "Soccer Team"
    email = "not-present@example.com"

    # ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 404
