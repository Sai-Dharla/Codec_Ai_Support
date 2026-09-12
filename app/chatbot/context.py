from typing import Dict, List, Optional, Any
from collections import deque
import time

class ConversationTurn:
    def __init__(self, user_message: str, bot_response: str, topic: Optional[str], intent: Optional[str]):
        self.user_message = user_message
        self.bot_response = bot_response
        self.topic = topic
        self.intent = intent
        self.timestamp = time.time()

class SessionContext:
    def __init__(self, session_id: str, max_turns: int = 5):
        self.session_id = session_id
        self.max_turns = max_turns
        self.active_topic: Optional[str] = None
        self.active_intent: Optional[str] = None
        self.history: deque = deque(maxlen=max_turns)
        self.entities: Dict[str, Any] = {}

    def add_turn(self, user_message: str, bot_response: str, topic: Optional[str], intent: Optional[str]):
        turn = ConversationTurn(user_message, bot_response, topic, intent)
        self.history.append(turn)
        if topic:
            self.active_topic = topic
        if intent:
            self.active_intent = intent

    def get_last_topic(self) -> Optional[str]:
        return self.active_topic

    def clear(self):
        self.history.clear()
        self.active_topic = None
        self.active_intent = None
        self.entities.clear()

class ContextManager:
    """Manages multi-turn conversation contexts and resolves coreferences/follow-ups."""
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self.sessions: Dict[str, SessionContext] = {}

    def get_or_create_session(self, session_id: str) -> SessionContext:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionContext(session_id, self.max_turns)
        return self.sessions[session_id]

    def is_likely_followup(self, user_message: str, nlp_processor) -> bool:
        """
        Detects if a user query is an elliptical or follow-up question referencing previous context.
        e.g., 'What if I don't receive the email?', 'Why?', 'How long does it take?', 'And what about returns?'
        """
        clean_msg = user_message.lower().strip()
        
        # Pronouns or reference indicators indicating follow-up
        reference_indicators = [
            "the email", "that email", "the link", "this link", "that link", "the code",
            "what if i", "what if it", "how long does it", "how long is it", "does it",
            "is it", "can it", "why not", "what about", "and if", "where is it",
            "still not", "didn't get it", "did not get it", "not received"
        ]
        
        for indicator in reference_indicators:
            if indicator in clean_msg:
                return True
                
        # If the message is very short and starts with interrogatives without concrete subject nouns
        keywords = nlp_processor.extract_keywords(clean_msg)
        if len(keywords) <= 3:
            interrogative_starters = ("what if", "how long", "why", "when", "how much", "what about", "is it")
            if any(clean_msg.startswith(starter) for starter in interrogative_starters):
                return True

        return False

    def resolve_context(self, session_id: str, user_message: str, nlp_processor) -> Optional[str]:
        session = self.get_or_create_session(session_id)
        if not session.active_topic:
            return None
        if self.is_likely_followup(user_message, nlp_processor):
            return session.active_topic
        return None

