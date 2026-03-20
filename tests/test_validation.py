"""
Tests for validation and error handling in the Mergington High School Activities API.
Tests follow the AAA (Arrange-Act-Assert) pattern.
Covers business logic validation, error responses, and edge cases.
Uses the client fixture from conftest.py.
"""

import pytest


class TestSignupValidation:
    """Tests for signup endpoint validation and error handling."""

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Prepare to sign up for an activity that doesn't exist
        Act: Send POST request with invalid activity name
        Assert: Response status should be 404 with appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        endpoint = f"/activities/{activity_name}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """
        Arrange: Use an email already signed up for an activity
        Act: Try to sign up the same email again
        Assert: Response status should be 400 with duplicate signup error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        endpoint = f"/activities/{activity_name}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_same_email_different_activities_allowed(self, client):
        """
        Arrange: Sign up a student for one activity, then try another
        Act: Post signup for different activity with same email
        Assert: Should succeed (same student can join multiple activities)
        """
        # Arrange
        email = "multiactive@mergington.edu"
        activity1_endpoint = "/activities/Chess%20Club/signup"
        activity2_endpoint = "/activities/Gym%20Class/signup"

        # Act - First signup
        response1 = client.post(activity1_endpoint, params={"email": email})
        # Second signup
        response2 = client.post(activity2_endpoint, params={"email": email})

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_signup_empty_email_string(self, client):
        """
        Arrange: Prepare to signup with an empty email
        Act: Send request with empty email parameter
        Assert: Request should succeed (no validation enforced on email format)
        """
        # Arrange
        activity_name = "Programming Class"
        email = ""
        endpoint = f"/activities/{activity_name}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        # Currently the API accepts any string, including empty ones
        assert response.status_code == 200

    def test_signup_plain_string_email(self, client):
        """
        Arrange: Sign up with a simple plain text email
        Act: Post request with plain string email
        Assert: Should succeed (no email format validation)
        """
        # Arrange
        activity_name = "Programming Class"
        email = "simpleemail"
        endpoint = f"/activities/{activity_name}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})

        # Assert
        assert response.status_code == 200


class TestRemoveParticipantValidation:
    """Tests for remove participant endpoint validation and error handling."""

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Prepare to remove from an activity that doesn't exist
        Act: Send DELETE request with invalid activity name
        Assert: Response status should be 404 with appropriate error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        endpoint = f"/activities/{activity_name}/participants/{email}"

        # Act
        response = client.delete(endpoint)

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_remove_non_enrolled_participant_returns_404(self, client):
        """
        Arrange: Use an email not enrolled in the activity
        Act: Send DELETE request
        Assert: Response status should be 404 with "not signed up" error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"
        endpoint = f"/activities/{activity_name}/participants/{email}"

        # Act
        response = client.delete(endpoint)

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_remove_participant_with_url_encoded_activity_name(self, client):
        """
        Arrange: Remove from activity with spaces in name (URL encoded)
        Act: Send DELETE with encoded activity name
        Assert: Should successfully remove participant
        """
        # Arrange
        activity_name_encoded = "Gym%20Class"
        email = "olivia@mergington.edu"  # Already in Gym Class
        endpoint = f"/activities/{activity_name_encoded}/participants/{email}"

        # Act
        response = client.delete(endpoint)

        # Assert
        assert response.status_code == 200

    def test_remove_same_participant_twice_fails_second_time(self, client):
        """
        Arrange: Remove a participant, then try to remove them again
        Act: First DELETE succeeds, second DELETE should fail
        Assert: First should be 200, second should be 404
        """
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        endpoint = f"/activities/{activity_name}/participants/{email}"

        # Act - First removal
        response1 = client.delete(endpoint)
        # Second removal attempt
        response2 = client.delete(endpoint)

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 404


class TestDataConsistency:
    """Tests to ensure data consistency across operations."""

    def test_signup_does_not_duplicate_in_list(self, client):
        """
        Arrange: Sign up a new participant
        Act: Fetch activities after signup
        Assert: Participant appears exactly once in the list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "testdup@mergington.edu"
        signup_endpoint = f"/activities/{activity_name}/signup"
        get_endpoint = "/activities"

        # Act
        client.post(signup_endpoint, params={"email": email})
        response = client.get(get_endpoint)
        activities = response.json()
        participants = activities[activity_name]["participants"]

        # Assert
        count = participants.count(email)
        assert count == 1

    def test_participant_count_reflects_actual_participants(self, client):
        """
        Arrange: Get initial participant count
        Act: Add and remove participants
        Assert: Participant count should always match actual list length
        """
        # Arrange
        activity_name = "Programming Class"
        get_endpoint = "/activities"

        # Act
        response = client.get(get_endpoint)
        activities = response.json()
        initial_count = len(activities[activity_name]["participants"])

        # Add a participant
        email_add = "newperson@mergington.edu"
        client.post(f"/activities/{activity_name}/signup", params={"email": email_add})

        response = client.get(get_endpoint)
        activities = response.json()
        after_add_count = len(activities[activity_name]["participants"])

        # Assert
        assert after_add_count == initial_count + 1

    def test_remove_updates_participant_list_correctly(self, client):
        """
        Arrange: Get initial participant list
        Act: Remove a participant
        Assert: Participant count should decrease by 1
        """
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        get_endpoint = "/activities"

        response = client.get(get_endpoint)
        activities = response.json()
        initial_count = len(activities[activity_name]["participants"])

        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.get(get_endpoint)
        activities = response.json()
        after_remove_count = len(activities[activity_name]["participants"])

        # Assert
        assert after_remove_count == initial_count - 1


class TestResponseFormats:
    """Tests to ensure API returns correctly formatted responses."""

    def test_signup_success_response_format(self, client):
        """
        Arrange: Prepare a successful signup
        Act: Send signup request
        Assert: Response should contain 'message' key
        """
        # Arrange
        activity_name = "Programming Class"
        email = "resptest@mergington.edu"
        endpoint = f"/activities/{activity_name}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})
        data = response.json()

        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_remove_success_response_format(self, client):
        """
        Arrange: Prepare a successful participant removal
        Act: Send delete request
        Assert: Response should contain 'message' key
        """
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"
        endpoint = f"/activities/{activity_name}/participants/{email}"

        # Act
        response = client.delete(endpoint)
        data = response.json()

        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)

    def test_error_response_contains_detail(self, client):
        """
        Arrange: Set up a request that will fail
        Act: Send invalid signup request
        Assert: Error response should contain 'detail' key
        """
        # Arrange
        activity_name = "Invalid Activity"
        email = "test@mergington.edu"
        endpoint = f"/activities/{activity_name}/signup"

        # Act
        response = client.post(endpoint, params={"email": email})
        data = response.json()

        # Assert
        assert "detail" in data
        assert isinstance(data["detail"], str)
