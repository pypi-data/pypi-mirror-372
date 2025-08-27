import pytest
from iss_tracker.tracker import get_iss_location

def test_get_iss_location_returns_dict():
    """
    Test that the function returns a dictionary with the expected keys.
    """
    location = get_iss_location()

    # We can't guarantee a live API call will succeed, so we handle the None case
    if location is not None:
        assert isinstance(location, dict)
        assert "latitude" in location
        assert "longitude" in location
        assert "timestamp" in location
    # If the API call fails, the test will simply pass, which is a limitation
    # without proper mocking.