"""
Pytest configuration and fixtures for the Mergington High School Activities API tests.
Provides TestClient and fresh activity data for each test.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
import src.app as app_module


# Define fresh activities template
FRESH_ACTIVITIES_TEMPLATE = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
}


@pytest.fixture(autouse=True)
def reset_activities_before_each_test():
    """
    Automatically reset the app's activities to fresh state before each test.
    This ensures tests don't interfere with each other via shared state.
    """
    # Clear and repopulate the activities dict (maintaining reference)
    app_module.activities.clear()
    app_module.activities.update(deepcopy(FRESH_ACTIVITIES_TEMPLATE))
    yield


@pytest.fixture
def client():
    """
    Fixture that provides a FastAPI TestClient for making requests to the API.
    The activities state is automatically reset before this fixture is used
    due to the reset_activities_before_each_test autouse fixture.
    """
    return TestClient(app_module.app)
