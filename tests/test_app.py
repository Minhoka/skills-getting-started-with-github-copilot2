import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Preserve the global `activities` dict between tests.
    Each test starts with a fresh copy of the original data.
    """
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all():
    # Arrange
    expected = copy.deepcopy(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_for_activity_success():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Signed up {email} for {activity}"
    assert email in activities[activity]["participants"]


def test_signup_duplicate_raises_bad_request():
    # Arrange
    activity = "Chess Club"
    existing_email = activities[activity]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_invalid_activity_raises_not_found():
    # Arrange
    activity = "Nonexistent Club"
    email = "someone@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    # Arrange
    activity = "Chess Club"
    participant = activities[activity]["participants"][0]
    assert participant in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": participant})

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Removed {participant} from {activity}"
    assert participant not in activities[activity]["participants"]


def test_remove_participant_not_registered():
    # Arrange
    activity = "Chess Club"
    email = "notregistered@mergington.edu"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_remove_from_invalid_activity():
    # Arrange
    activity = "Ghost Activity"
    email = "nobody@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"