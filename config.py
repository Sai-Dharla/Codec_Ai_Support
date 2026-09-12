import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent
load_dotenv(basedir / '.env')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'codec-technologies-chatbot-secret-key-2026')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', str(basedir / 'data' / 'chatbot.db'))
    FAQS_PATH = os.environ.get('FAQS_PATH', str(basedir / 'data' / 'faqs.json'))
    
    # Model configuration (Lightweight and CPU-friendly)
    TRANSFORMER_MODEL_NAME = os.environ.get(
        'TRANSFORMER_MODEL_NAME', 
        'sentence-transformers/all-MiniLM-L6-v2'
    )
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = float(os.environ.get('HIGH_CONFIDENCE_THRESHOLD', '0.65'))
    LOW_CONFIDENCE_THRESHOLD = float(os.environ.get('LOW_CONFIDENCE_THRESHOLD', '0.40'))
    
    # Session context settings
    MAX_CONTEXT_TURNS = int(os.environ.get('MAX_CONTEXT_TURNS', '5'))

