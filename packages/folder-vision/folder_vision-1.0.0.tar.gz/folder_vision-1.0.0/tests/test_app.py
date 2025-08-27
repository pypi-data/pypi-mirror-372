from fastapi.testclient import TestClient
from folder_vision.app import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    # Root now returns HTML page; check for title marker
    assert b"Folder Vision" in r.content

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data
