import uuid
import logging
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, jsonify, current_app

logger = logging.getLogger(__name__)

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Renders the main customer support chatbot web interface."""
    return render_template('index.html')

@bp.route('/api/chat', methods=['POST'])
def chat():
    """
    Main Chatbot API endpoint.
    Accepts JSON: { "message": "user input", "session_id": "optional-uuid" }
    Returns: { "response": str, "session_id": str, "intent": str, "confidence": float, "timestamp": str, "context_topic": str }
    """
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id', '').strip()
    
    # Generate new session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
        
    if not user_message:
        return jsonify({
            "response": "Please type a message to start our conversation.",
            "session_id": session_id,
            "intent": "empty_input",
            "confidence": 1.0,
            "context_topic": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 400

    # Retrieve response generator and database instances from current_app
    chatbot_engine = current_app.chatbot_engine
    db = current_app.db

    try:
        # Generate context-aware response
        result = chatbot_engine.generate_response(session_id, user_message)
        
        bot_response = result['response']
        intent = result['intent']
        confidence = result['confidence']
        context_topic = result['context_topic']
        
        # Log interaction to SQLite database
        db.log_interaction(
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            intent_detected=intent,
            confidence=confidence,
            context_topic=context_topic
        )
        
        return jsonify({
            "response": bot_response,
            "session_id": session_id,
            "intent": intent,
            "confidence": confidence,
            "context_topic": context_topic,
            "is_fallback": result.get('is_fallback', False),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error handling chat request: {e}", exc_info=True)
        return jsonify({
            "response": "An internal error occurred while processing your request. Please try again shortly.",
            "session_id": session_id,
            "intent": "error",
            "confidence": 0.0,
            "context_topic": None,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@bp.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id: str):
    """Fetches stored conversation history for a given session from SQLite."""
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
        
    db = current_app.db
    history = db.get_session_history(session_id)
    return jsonify({
        "session_id": session_id,
        "history": history,
        "total_turns": len(history)
    })

@bp.route('/api/session/new', methods=['POST'])
def new_session():
    """Generates a fresh session ID and initializes session record."""
    session_id = str(uuid.uuid4())
    db = current_app.db
    db.create_or_update_session(session_id)
    return jsonify({
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

@bp.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint for deployment probes."""
    return jsonify({
        "status": "healthy",
        "service": "codec-ai-chatbot",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

