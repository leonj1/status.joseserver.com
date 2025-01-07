import pytest
import pytest_asyncio
from datetime import datetime, timedelta
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
    # Create 15 incidents
    incident_data = test_cases[0]["payload"]
    for i in range(15):
        incident_data["incident"]["title"] = f"Test Incident {i}"
        response = test_client.post("/incidents", json=incident_data)
        assert response.status_code == 200
    
    # Get recent incidents (default should be 10)
    response = test_client.get("/incidents/recent")
    assert response.status_code == 200
    
    incidents = response.json()
    assert len(incidents) == 10
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
    incident_data = test_cases[0]["payload"]
    
    # Create an old incident
    old_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
    response = test_client.post("/incidents", json=incident_data)
    assert response.status_code == 200
    
    # Create a recent incident
    response = test_client.post("/incidents", json=incident_data)
    assert response.status_code == 200
    
    # Get incidents after the old date
    response = test_client.get(f"/incidents/recent?start_date={old_date}")
    assert response.status_code == 200
    
    incidents = response.json()
    assert len(incidents) == 2
    
    # Get incidents with future date (should return empty list)
    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    response = test_client.get(f"/incidents/recent?start_date={future_date}")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_get_recent_incidents_count_limit(test_client):
    # Try to get more than maximum allowed incidents
    response = test_client.get("/incidents/recent?count=51")
    assert response.status_code == 422  # Validation error