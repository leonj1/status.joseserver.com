import pytest
import pytest_asyncio
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
            "created_at", "incident"
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