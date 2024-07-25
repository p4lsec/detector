from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_ip():
    response = client.get("/search?ip=1.1.1.1")
    assert response.status_code == 200
    assert isinstance(response.json(), bool)

def test_get_tor_exit_nodes():
    response = client.get("/list")
    assert response.status_code == 200
    assert "ips" in response.json()