import os
import json
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from .nlp import NLPProcessor
from .model import SemanticModel
from .context import ContextManager

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Coordinates the NLTK NLP processor, Hugging Face Transformer model,
    and Conversation Context Manager to generate context-aware, accurate responses.
    """
    def __init__(
        self,
        faqs_path: str,
        transformer_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2',
        high_threshold: float = 0.65,
        low_threshold: float = 0.40,
        max_context_turns: int = 5
    ):
        self.faqs_path = faqs_path
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        
        self.nlp = NLPProcessor()
        self.model = SemanticModel(model_name=transformer_model_name)
        self.context_manager = ContextManager(max_turns=max_context_turns)
        
        self.faqs: List[Dict[str, Any]] = []
        self.pattern_records: List[Dict[str, Any]] = []
        self.pattern_embeddings: Optional[np.ndarray] = None
        
        self._load_and_index_faqs()

    def _load_and_index_faqs(self):
        """Loads FAQs from JSON and builds index + dense semantic embeddings."""
        if not os.path.exists(self.faqs_path):
            raise FileNotFoundError(f"FAQ file not found at: {self.faqs_path}")

        with open(self.faqs_path, 'r', encoding='utf-8') as f:
            self.faqs = json.load(f)

        self.pattern_records = []
        all_pattern_texts = []

        for faq in self.faqs:
            faq_id = faq.get('id')
            topic = faq.get('context_topic', faq_id)
            response = faq.get('response')
            
            # Index main patterns
            for pattern in faq.get('patterns', []):
                cleaned = self.nlp.clean_text(pattern)
                keywords = self.nlp.extract_keywords(pattern)
                self.pattern_records.append({
                    'faq_id': faq_id,
                    'topic': topic,
                    'pattern_text': pattern,
                    'cleaned_text': cleaned,
                    'keywords': keywords,
                    'response': response,
                    'is_followup': False,
                    'requires_context': None
                })
                all_pattern_texts.append(pattern)

            # Index follow-up patterns
            for follow_up in faq.get('follow_ups', []):
                fu_resp = follow_up.get('response')
                req_ctx = follow_up.get('requires_context', topic)
                for fu_pattern in follow_up.get('patterns', []):
                    cleaned = self.nlp.clean_text(fu_pattern)
                    keywords = self.nlp.extract_keywords(fu_pattern)
                    self.pattern_records.append({
                        'faq_id': faq_id,
                        'topic': topic,
                        'pattern_text': fu_pattern,
                        'cleaned_text': cleaned,
                        'keywords': keywords,
                        'response': fu_resp,
                        'is_followup': True,
                        'requires_context': req_ctx
                    })
                    all_pattern_texts.append(fu_pattern)

        logger.info(f"Encoding {len(all_pattern_texts)} FAQ patterns with Hugging Face Transformers...")
        self.pattern_embeddings = self.model.encode(all_pattern_texts)
        logger.info("FAQ pattern indexing completed.")

    def generate_response(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Processes the user message through NLP, Context Resolver, and Transformers Semantic Matcher.
        Returns a response dictionary with response text, intent, confidence, and context topic.
        """
        clean_query = self.nlp.clean_text(user_message)
        if not clean_query:
            return {
                "response": "I didn't receive any message. How can I assist you with your account, orders, or support questions?",
                "intent": "empty_input",
                "confidence": 1.0,
                "context_topic": None,
                "is_fallback": False
            }

        session = self.context_manager.get_or_create_session(session_id)
        active_topic = session.get_last_topic()
        is_followup_query = self.context_manager.is_likely_followup(user_message, self.nlp)
        query_keywords = self.nlp.extract_keywords(user_message)

        # 1. Hugging Face Transformer Semantic Similarity
        query_embedding = self.model.encode([user_message])
        similarities = self.model.compute_similarity(query_embedding, self.pattern_embeddings)

        # 2. Hybrid Scoring with Context Weighting and NLTK Overlap
        best_score = -1.0
        best_match = None

        for idx, record in enumerate(self.pattern_records):
            semantic_score = float(similarities[idx])
            nltk_overlap = self.nlp.compute_token_overlap(query_keywords, record['keywords'])
            
            # Combined base score: 80% Transformer semantic similarity + 20% NLTK keyword overlap
            combined_score = 0.80 * semantic_score + 0.20 * nltk_overlap

            # Context boost / penalty
            if record['is_followup']:
                if active_topic and record['requires_context'] == active_topic:
                    # Boost relevance when current conversation context matches follow-up requirement
                    if is_followup_query:
                        combined_score += 0.25
                    else:
                        combined_score += 0.10
                else:
                    # Penalize follow-up responses if the active context is absent or different
                    combined_score -= 0.30
            else:
                # Main question pattern
                if active_topic and record['topic'] == active_topic and is_followup_query:
                    combined_score += 0.05

            if combined_score > best_score:
                best_score = combined_score
                best_match = record

        # Cap confidence between 0.0 and 1.0
        final_confidence = max(0.0, min(1.0, float(best_score)))

        # 3. Confidence Threshold Decision Logic
        if best_match and final_confidence >= self.high_threshold:
            # High confidence: return matched answer
            response_text = best_match['response']
            detected_intent = best_match['faq_id']
            new_topic = best_match['topic']
            is_fallback = False
            session.add_turn(user_message, response_text, new_topic, detected_intent)
        elif best_match and final_confidence >= self.low_threshold:
            # Medium confidence: provide answer with helpful clarification suggestion
            response_text = (
                f"{best_match['response']}\n\n"
                f"*(Note: If you were asking about something else, please let me know or contact support@company.com)*"
            )
            detected_intent = best_match['faq_id']
            new_topic = best_match['topic']
            is_fallback = False
            session.add_turn(user_message, response_text, new_topic, detected_intent)
        else:
            # Low confidence: trigger intelligent fallback
            detected_intent = "fallback_unknown"
            new_topic = active_topic
            is_fallback = True
            
            if active_topic == "password_reset":
                response_text = (
                    "I'm not quite sure about that regarding password reset. "
                    "You can reset your password using the 'Forgot Password' link on the login page. "
                    "If you're having trouble receiving emails, please check your spam folder or contact our support desk."
                )
            elif active_topic == "order_tracking":
                response_text = (
                    "I couldn't find exact details for your order question. "
                    "You can track any active order in your dashboard under 'My Orders', or reach out to our team with your Order ID."
                )
            elif active_topic == "refund_policy":
                response_text = (
                    "I'm not completely sure about that specific return inquiry. "
                    "Our general return policy allows returns within 30 days. For personalized assistance, contact support@company.com."
                )
            else:
                response_text = (
                    "I'm sorry, I didn't quite understand your request. "
                    "I can assist you with password resets, account registration, order tracking, returns & refunds, and payment methods. "
                    "Could you please rephrase your question, or ask to speak with human support?"
                )

        return {
            "response": response_text,
            "intent": detected_intent,
            "confidence": round(final_confidence, 4),
            "context_topic": new_topic,
            "is_fallback": is_fallback
        }

