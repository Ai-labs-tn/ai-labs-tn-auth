from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.api.health import router   # adjust import based on your project structure

# Create a FastAPI app for testing and include the router
app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health/")
    
    # Validate HTTP status
    assert response.status_code == 200
    
    # Validate response type
    data = response.json()
    assert isinstance(data, dict)
    
    # Expected keys in response
    assert data["ok"] is True
    assert data["service"] == "ai-labs-tn-api"
