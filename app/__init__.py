import os
import logging
from flask import Flask
from config import Config
from app.database.db import Database
from app.chatbot.response import ResponseGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_class=Config) -> Flask:
    """Application factory for Flask AI Chatbot application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLite database
    logger.info(f"Initializing SQLite database at: {app.config['DATABASE_PATH']}")
    db = Database(app.config['DATABASE_PATH'])
    app.db = db

    # Initialize AI Chatbot engine (NLTK + Hugging Face Transformers)
    logger.info("Initializing AI Chatbot engine...")
    chatbot_engine = ResponseGenerator(
        faqs_path=app.config['FAQS_PATH'],
        transformer_model_name=app.config['TRANSFORMER_MODEL_NAME'],
        high_threshold=app.config['HIGH_CONFIDENCE_THRESHOLD'],
        low_threshold=app.config['LOW_CONFIDENCE_THRESHOLD'],
        max_context_turns=app.config['MAX_CONTEXT_TURNS']
    )
    app.chatbot_engine = chatbot_engine
    logger.info("Chatbot engine initialized successfully.")

    # Register Blueprint routes
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app

