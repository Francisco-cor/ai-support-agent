from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'

def test_chat_empty():
    r = client.post('/chat', json={'query': ''})
    assert r.status_code == 400
