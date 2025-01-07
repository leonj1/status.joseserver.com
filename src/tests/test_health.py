import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app

test_cases = [
    {
        "name": "health check returns 200",
        "endpoint": "/health",
        "expected_status": 200,
        "expected_fields": ["status", "version", "timestamp"]
    }
]

@pytest.fixture
def client():
    """
    Test client fixture that ensures proper application lifecycle.
    """
    with TestClient(app) as client:
        # The TestClient context manager handles the lifespan events
        yield client

@pytest.mark.parametrize("test_case", test_cases, ids=lambda t: t["name"])
def test_health_endpoint(client, test_case):
    response = client.get(test_case["endpoint"])
    
    # Check status code
    assert response.status_code == test_case["expected_status"]
    
    # Check response structure
    data = response.json()
    for field in test_case["expected_fields"]:
        assert field in data
    
    # Check specific values
    assert data["status"] == "healthy"
    assert data["version"] == app.version
    assert isinstance(data["timestamp"], str)
    
    # Verify timestamp is a valid datetime string
    datetime.fromisoformat(data["timestamp"])