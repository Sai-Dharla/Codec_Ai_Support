import os
import json
import pytest
from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    DATABASE_PATH = "data/test_chatbot.db"

@pytest.fixture(scope="module")
def app():
    app = create_app(TestConfig)
    yield app
    if os.path.exists("data/test_chatbot.db"):
        try:
            os.remove("data/test_chatbot.db")
        except Exception:
            pass

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_new_session(client):
    response = client.post('/api/session/new')
    assert response.status_code == 200
    data = response.get_json()
    assert 'session_id' in data

def test_chat_empty_message(client):
    response = client.post('/api/chat', json={"message": "", "session_id": "test-session"})
    assert response.status_code == 400

def test_password_reset_and_contextual_followup(client):
    session_id = "test-context-session-001"
    
    # 1. Main inquiry: Password reset
    res1 = client.post('/api/chat', json={
        "message": "How can I reset my password?",
        "session_id": session_id
    })
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert data1['intent'] == 'password_reset'
    assert "Forgot Password" in data1['response']
    assert data1['confidence'] >= 0.65
    assert data1['context_topic'] == 'password_reset'

    # 2. Contextual follow-up: "What if I don't receive the email?"
    res2 = client.post('/api/chat', json={
        "message": "What if I don't receive the email?",
        "session_id": session_id
    })
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert "Spam" in data2['response'] or "email" in data2['response'].lower()
    assert data2['context_topic'] == 'password_reset'

    # 3. Check conversation history in database
    history_res = client.get(f'/api/history/{session_id}')
    assert history_res.status_code == 200
    history_data = history_res.get_json()
    assert history_data['total_turns'] == 2

def test_order_tracking_and_followup(client):
    session_id = "test-order-session-002"
    
    res1 = client.post('/api/chat', json={
        "message": "Where is my order?",
        "session_id": session_id
    })
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert data1['intent'] == 'order_tracking'
    assert "Track Order" in data1['response']

    res2 = client.post('/api/chat', json={
        "message": "What if the tracking number doesn't work?",
        "session_id": session_id
    })
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert "24 hours" in data2['response'] or "tracking" in data2['response'].lower()

def test_fallback_unclear_query(client):
    session_id = "test-fallback-session-003"
    res = client.post('/api/chat', json={
        "message": "xyzqwerty nonsense query 991823",
        "session_id": session_id
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['is_fallback'] is True
    assert "didn't quite understand" in data['response'] or "rephrase" in data['response']

