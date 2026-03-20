"""
Tests for FastAPI endpoints of the Mergington High School Activities API.
Tests follow the AAA (Arrange-Act-Assert) pattern.
Uses the client fixture from conftest.py.
"""

import pytest


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """
        Arrange: Set up a GET request to /activities
        Act: Make the request
        Assert: Response status code should be 200
        """
        # Arrange
        endpoint = "/activities"

        # Act
        response = client.get(endpoint)

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """
        Arrange: Prepare to fetch activities
        Act: Call GET /activities
        Assert: Response should be a dictionary
        """
        # Arrange
        endpoint = "/activities"

        # Act
        response = client.get(endpoint)
        data = response.json()

        # Assert
        assert isinstance(data, dict)

    def test_get_activities_contains_all_required_fields(self, client):
        """
        Arrange: Fetch activities
        Act: Get the activities response
        Assert: Each activity has all required fields
        """
        # Arrange
        endpoint = "/activities"
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get(endpoint)
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields

    def test_get_activities_participants_is_list(self, client):
        """
        Arrange: Get activities from API
        Act: Fetch and parse response
        Assert: Each activity's participants field is a list
        """
        # Arrange
        endpoint = "/activities"

        # Act
        response = client.get(endpoint)
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Set up a GET request to /
        Act: Make the request (follow_redirects=False to see redirect)
        Assert: Should return 307 Temporary Redirect status
        """
        # Arrange
        endpoint = "/"

        # Act
        response = client.get(endpoint, follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful_new_participant(self, client):
        """
        Arrange: Use an existing activity and a new email
        Act: Post to signup endpoint
        Assert: Response status should be 200 and message should confirm signup
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        endpoint = f"/activities/{activity_name}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """
        Arrange: Prepare to sign up a student
        Act: Sign up student, then fetch activities
        Assert: New participant should appear in activities list
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newemail@mergington.edu"
        signup_endpoint = f"/activities/{activity_name}/signup"
        get_endpoint = "/activities"

        # Act
        client.post(signup_endpoint, params={"email": email})
        response = client.get(get_endpoint)
        activities = response.json()

        # Assert
        assert email in activities[activity_name]["participants"]

    def test_signup_with_url_encoded_activity_name(self, client):
        """
        Arrange: Use an activity with spaces (needs URL encoding)
        Act: Sign up with encoded activity name
        Assert: Should successfully sign up
        """
        # Arrange
        activity_name = "Chess Club"
        email = "test@mergington.edu"
        encoded_activity = "Chess%20Club"
        endpoint = f"/activities/{encoded_activity}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200


class TestRemoveParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_participant_successful(self, client):
        """
        Arrange: Set up to remove an existing participant
        Act: Send DELETE request
        Assert: Response status should be 200 and message should confirm removal
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        endpoint = f"/activities/{activity_name}/participants/{email}"

        # Act
        response = client.delete(endpoint)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_remove_participant_removes_from_list(self, client):
        """
        Arrange: Identify a participant in an activity
        Act: Remove the participant, then fetch activities
        Assert: Participant should no longer be in the list
        """
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"  # Already in Gym Class
        delete_endpoint = f"/activities/{activity_name}/participants/{email}"
        get_endpoint = "/activities"

        # Act
        client.delete(delete_endpoint)
        response = client.get(get_endpoint)
        activities = response.json()

        # Assert
        assert email not in activities[activity_name]["participants"]

    def test_remove_participant_with_url_encoded_email(self, client):
        """
        Arrange: Use an email with special characters (if needed)
        Act: Send DELETE request with encoded email
        Assert: Should successfully remove participant
        """
        # Arrange
        activity_name = "Chemistry Club"
        email = "test@example.com"
        # First signup a participant
        signup_endpoint = f"/activities/Programming Class/signup"
        client.post(signup_endpoint, params={"email": email})
        
        # Now remove them
        encoded_email = "test%40example.com"
        delete_endpoint = f"/activities/Programming Class/participants/{encoded_email}"

        # Act
        response = client.delete(delete_endpoint)

        # Assert
        assert response.status_code == 200
