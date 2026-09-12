import os
import tempfile
import pytest
from app.database.db import Database, init_db

@pytest.fixture
def temp_db():
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    db_path = temp_file.name
    db = Database(db_path)
    yield db
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except Exception:
        pass

def test_db_initialization(temp_db):
    assert os.path.exists(temp_db.db_path)

def test_session_lifecycle(temp_db):
    session_id = "test-session-123"
    temp_db.create_or_update_session(session_id, context_topic="password_reset")
    
    context = temp_db.get_session_context(session_id)
    assert context == "password_reset"

def test_log_interaction_and_history(temp_db):
    session_id = "test-session-456"
    
    temp_db.log_interaction(
        session_id=session_id,
        user_message="How can I reset my password?",
        bot_response="You can reset your password on the login page.",
        intent_detected="password_reset",
        confidence=0.92,
        context_topic="password_reset"
    )

    temp_db.log_interaction(
        session_id=session_id,
        user_message="What if I don't receive the email?",
        bot_response="Check your spam folder.",
        intent_detected="password_reset",
        confidence=0.88,
        context_topic="password_reset"
    )

    history = temp_db.get_session_history(session_id)
    assert len(history) == 2
    assert history[0]["user_message"] == "How can I reset my password?"
    assert history[0]["intent_detected"] == "password_reset"
    assert history[1]["user_message"] == "What if I don't receive the email?"
    assert history[1]["bot_response"] == "Check your spam folder."

