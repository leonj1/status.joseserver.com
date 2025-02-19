import pytest
import pytest_asyncio
import time
from datetime import datetime, timedelta

def wait(seconds):
    """Helper function to add delay between operations"""
    time.sleep(seconds)
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.main import app, get_db

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest_asyncio.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def override_get_db(db_session):
    async def _override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def test_client(override_get_db):
    with TestClient(app) as client:
        yield client

test_cases = [
    {
        "name": "valid incident creation",
        "payload": {
            "service": "Test Service",
            "previous_state": "OK",
            "current_state": "MINOR",
            "incident": {
                "title": "Test Incident",
                "description": "This is a test incident",
                "components": ["Component1", "Component2"],
                "url": "https://status.test-service.com/incident-1"
            }
        },
        "expected_status": 200,
        "expected_fields": [
            "id", "service", "previous_state", "current_state",
            "created_at", "incident", "history"
        ]
    },
    {
        "name": "invalid URL format",
        "payload": {
            "service": "Test Service",
            "previous_state": "OK",
            "current_state": "MINOR",
            "incident": {
                "title": "Test Incident",
                "description": "This is a test incident",
                "components": ["Component1", "Component2"],
                "url": "not-a-url"
            }
        },
        "expected_status": 422
    }
]

@pytest.mark.parametrize("test_case", test_cases, ids=lambda t: t["name"])
def test_create_incident(test_case, test_client):
    response = test_client.post("/incidents", json=test_case["payload"])
    
    assert response.status_code == test_case["expected_status"]
    
    if test_case["expected_status"] == 200:
        data = response.json()
        # Check all expected fields are present
        for field in test_case["expected_fields"]:
            assert field in data
        
        # Verify the data matches the input
        assert data["service"] == test_case["payload"]["service"]
        assert data["previous_state"] == test_case["payload"]["previous_state"]
        assert data["current_state"] == test_case["payload"]["current_state"]
        
        # Verify incident details
        incident = data["incident"]
        assert incident["title"] == test_case["payload"]["incident"]["title"]
        assert incident["description"] == test_case["payload"]["incident"]["description"]
        assert incident["components"] == test_case["payload"]["incident"]["components"]
        assert incident["url"] == test_case["payload"]["incident"]["url"]
        
        # Verify history was created
        assert "history" in data
        assert len(data["history"]) == 1
        history_entry = data["history"][0]
        assert history_entry["service"] == test_case["payload"]["service"]
        assert history_entry["previous_state"] == test_case["payload"]["previous_state"]
        assert history_entry["current_state"] == test_case["payload"]["current_state"]
        assert "recorded_at" in history_entry

def test_get_incident_history(test_client):
    # First create an incident
    incident_data = test_cases[0]["payload"]
    response = test_client.post("/incidents", json=incident_data)
    assert response.status_code == 200
    incident_id = response.json()["id"]
    
    # Get the history
    response = test_client.get(f"/incidents/{incident_id}/history")
    assert response.status_code == 200
    
    history = response.json()
    assert isinstance(history, list)
    assert len(history) == 1
    
    entry = history[0]
    assert entry["incident_id"] == incident_id
    assert entry["service"] == incident_data["service"]
    assert entry["previous_state"] == incident_data["previous_state"]
    assert entry["current_state"] == incident_data["current_state"]
    assert "recorded_at" in entry

def test_get_recent_incidents_default(test_client):
    # Create 15 incidents with small delays to ensure distinct timestamps
    incident_data = test_cases[0]["payload"].copy()
    created_incidents = []
        
    for i in range(15):
        incident_data["incident"] = test_cases[0]["payload"]["incident"].copy()
        incident_data["service"] = f"Service {i}"  # Different service for each incident
        incident_data["incident"]["title"] = f"Test Incident {i}"
        created_incidents.append({
            "service": incident_data["service"],
            "title": incident_data["incident"]["title"]
        })
        response = test_client.post("/incidents", json=incident_data)
        assert response.status_code == 200
        # Small delay to ensure distinct timestamps
        wait(0.1)
    
    # Get recent incidents with explicit count=10
    response = test_client.get("/incidents/recent?count=10")
    assert response.status_code == 200
    
    incidents = response.json()
    assert len(incidents) == 10
    
    # Verify we got the 10 most recent incidents (last 10 we created)
    received_incidents = set((inc["service"], inc["incident"]["title"]) for inc in incidents)
    expected_incidents = set((inc["service"], inc["title"]) for inc in created_incidents[-10:])
    assert received_incidents == expected_incidents
    
    # Verify they're in reverse chronological order
    for i in range(len(incidents) - 1):
        current = datetime.fromisoformat(incidents[i]["created_at"])
        next_incident = datetime.fromisoformat(incidents[i + 1]["created_at"])
        assert current >= next_incident

def test_get_recent_incidents_with_count(test_client):
    # Create 5 incidents
    incident_data = test_cases[0]["payload"]
    for i in range(5):
        incident_data["incident"]["title"] = f"Test Incident {i}"
        response = test_client.post("/incidents", json=incident_data)
        assert response.status_code == 200
    
    # Get recent incidents with count=3
    response = test_client.get("/incidents/recent?count=3")
    assert response.status_code == 200
    
    incidents = response.json()
    assert len(incidents) == 3

def test_get_recent_incidents_with_date(test_client):
    # Create incidents with different dates
    incident_data = test_cases[0]["payload"].copy()
    
    # Create an old incident
    incident_data["incident"] = test_cases[0]["payload"]["incident"].copy()
    incident_data["incident"]["title"] = "Old Incident"
    response = test_client.post("/incidents", json=incident_data)
    assert response.status_code == 200
    old_incident = response.json()
    wait(0.1)  # Ensure distinct timestamps
    
    # Record the timestamp after the first incident but before the second
    middle_date = datetime.utcnow().isoformat()
    wait(0.1)  # Ensure distinct timestamps
    
    # Create a recent incident
    incident_data["incident"]["title"] = "Recent Incident"
    response = test_client.post("/incidents", json=incident_data)
    assert response.status_code == 200
    recent_incident = response.json()
    
    # Get incidents after the middle date (should only get the recent one)
    response = test_client.get(f"/incidents/recent?start_date={middle_date}")
    assert response.status_code == 200
    
    incidents = response.json()
    assert len(incidents) == 1
    assert incidents[0]["incident"]["title"] == "Recent Incident"
    
    # Get incidents with future date (should return empty list)
    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    response = test_client.get(f"/incidents/recent?start_date={future_date}")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_get_recent_incidents_count_limit(test_client):
    # Try to get more than maximum allowed incidents
    response = test_client.get("/incidents/recent?count=51")
    assert response.status_code == 422  # Validation error

def test_get_recent_incidents_latest_per_service(test_client):
    # Create multiple incidents for the same service
    service_a_incidents = [
        {
            "service": "Service A",
            "previous_state": "operational",
            "current_state": "outage",
            "incident": {
                "title": "Service A Outage",
                "description": "Initial outage",
                "components": ["Component1"],
                "url": "https://status.test-service.com/incident-1"
            }
        },
        {
            "service": "Service A",
            "previous_state": "outage",
            "current_state": "degraded",
            "incident": {
                "title": "Service A Degraded",
                "description": "Partially restored",
                "components": ["Component1"],
                "url": "https://status.test-service.com/incident-2"
            }
        },
        {
            "service": "Service A",
            "previous_state": "degraded",
            "current_state": "operational",
            "incident": {
                "title": "Service A Restored",
                "description": "Fully operational",
                "components": ["Component1"],
                "url": "https://status.test-service.com/incident-3"
            }
        }
    ]
    
    # Create incidents
    for incident in service_a_incidents:
        response = test_client.post("/incidents", json=incident)
        assert response.status_code == 200
    
    # Get recent incidents
    response = test_client.get("/incidents/recent")
    assert response.status_code == 200
    
    incidents = response.json()
    
    # Find Service A incidents
    service_a_incidents = [i for i in incidents if i["service"] == "Service A"]
    
    # Should only have one incident for Service A
    assert len(service_a_incidents) == 1
    # Should be the latest state (operational)
    assert service_a_incidents[0]["current_state"] == "operational"
