import pytest
from fastapi.testclient import TestClient

def test_app_initialization(app_with_db):
    """
    Test that the FastPluggy app initializes correctly.
    """
    app, fast_pluggy = app_with_db
    
    with TestClient(app=app, base_url="http://testserver") as client:
        response = client.get("/")
        # We're just testing that the app responds, not checking specific content
        assert response.status_code in (200, 302, 404), f"Unexpected status code: {response.status_code}"