import pytest
from app.chatbot.nlp import NLPProcessor

@pytest.fixture(scope="module")
def nlp():
    return NLPProcessor()

def test_clean_text(nlp):
    raw = "  Hello! Can I RESET my password???  "
    cleaned = nlp.clean_text(raw)
    assert cleaned == "hello! can i reset my password?"

def test_tokenize(nlp):
    text = "How can I reset my password?"
    tokens = nlp.tokenize(text)
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    assert "password" in [t.lower() for t in tokens]

def test_extract_keywords(nlp):
    text = "How can I reset my account password?"
    keywords = nlp.extract_keywords(text)
    # Stopwords like 'how', 'can', 'i', 'my' should be filtered
    assert "reset" in keywords
    assert "password" in keywords
    assert "how" not in keywords
    assert "i" not in keywords

def test_pos_tagging(nlp):
    text = "Reset password securely"
    tags = nlp.pos_tagging(text)
    assert len(tags) >= 2
    assert all(isinstance(t, tuple) and len(t) == 2 for t in tags)

def test_token_overlap(nlp):
    tokens_a = ["reset", "password", "email"]
    tokens_b = ["password", "email", "link"]
    overlap = nlp.compute_token_overlap(tokens_a, tokens_b)
    # Intersection = {'password', 'email'} (2), Union = {'reset', 'password', 'email', 'link'} (4) => 0.5
    assert overlap == pytest.approx(0.5)

    assert nlp.compute_token_overlap([], ["abc"]) == 0.0

