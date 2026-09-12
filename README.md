# AI-Powered Customer Support & FAQ Chatbot

A production-ready, context-aware AI Chatbot designed for customer support and FAQ automation. Built with **Python**, **NLTK**, **Hugging Face Transformers**, **Flask**, and **SQLite** as part of the **Codec Technologies Internship**.

---

## 📌 Project Overview

This project provides an intelligent customer support chatbot that uses dense semantic embeddings and Natural Language Processing (NLP) techniques to comprehend user intent, resolve elliptical follow-up questions using session context, and log interactions securely to a SQLite database.

### 🌟 Key Highlights
- **Semantic Intent Matching**: Uses `sentence-transformers/all-MiniLM-L6-v2` (Hugging Face) for fast, accurate semantic matching on CPU without needing huge GPU resources.
- **NLTK Pipeline**: Tokenization, lemmatization, stopword filtering, POS tagging, and token overlap scoring.
- **Multi-Turn Context Tracking**: Accurately handles context-dependent follow-up queries (e.g., `"How can I reset my password?"` followed by `"What if I don't receive the email?"`).
- **Confidence Thresholds**: Distinguishes high-confidence answers, medium-confidence suggestions, and graceful fallback responses for out-of-scope inquiries.
- **Persistent Interaction Logging**: Stores sessions and detailed conversation turns (session ID, user query, response, intent, confidence, context topic, timestamp) in SQLite.
- **Modern Responsive Web UI**: Clean, accessible chat interface with real-time feedback, quick prompt suggestions, and session reset.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core programming language |
| **NLP Pipeline** | NLTK | Tokenization, lemmatization, stopword removal, POS tagging |
| **AI Model** | Hugging Face Transformers (`all-MiniLM-L6-v2`) | Semantic embeddings and similarity scoring |
| **Backend Framework** | Flask | RESTful API endpoints and template serving |
| **Database** | SQLite3 | Persistent session and interaction logging |
| **Frontend** | HTML5, CSS3, Modern Vanilla JS | Responsive chat interface |
| **Testing** | Pytest | Automated unit and integration testing |
| **Production WSGI** | Gunicorn | Production-ready HTTP WSGI server |

---

## 📂 Project Structure

```text
ai-powered-chatbot/
│
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── routes.py            # API & web view routes
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── nlp.py           # NLTK tokenization & preprocessing
│   │   ├── model.py         # Hugging Face Transformer embeddings
│   │   ├── context.py       # Multi-turn dialogue context manager
│   │   └── response.py      # Response orchestration & thresholds
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py            # SQLite helper & query methods
│   │   └── models.py        # Data models
│   ├── templates/
│   │   └── index.html       # Chat web interface
│   └── static/
│       ├── css/
│       │   └── style.css    # Clean responsive styling
│       └── js/
│           └── chatbot.js   # Client-side chat logic
│
├── data/
│   ├── faqs.json            # Knowledge base with context branches
│   └── .gitkeep
│
├── tests/
│   ├── test_nlp.py          # NLTK pipeline tests
│   ├── test_database.py     # SQLite interaction logging tests
│   └── test_chatbot.py      # Multi-turn context & API tests
│
├── .env.example             # Environment template
├── .gitignore               # Git hygiene rules
├── app.py                   # Application entrypoint
├── config.py                # Configuration management
├── requirements.txt         # Project dependencies
├── Procfile                 # Cloud deployment config (Render / Heroku)
├── runtime.txt              # Deployment python version
└── README.md                # Documentation
```

---

## 🔄 Functional Architecture Flow

```text
       User Question
            │
            ▼
    [Web Chat Interface]
            │ (JSON over HTTP)
            ▼
       [Flask API]
            │
            ▼
   [NLTK NLP Pipeline] ──> Tokenize, Lemmatize, POS Tag, Filter Stopwords
            │
            ▼
  [Hugging Face Model] ──> Dense Embedding (`all-MiniLM-L6-v2`)
            │
            ▼
   [Context Manager]   ──> Detect active topic & follow-up coreference
            │
            ▼
  [Response Generator] ──> Hybrid scoring & Confidence threshold check
            │
            ▼
    [SQLite Database]  ──> Log Session ID, Message, Response, Intent, Timestamp
            │
            ▼
  [Return to UI Client]
```

---


## 👨‍💻 Internship Project Submission
Developed for the **Codec Technologies Internship**. Satisfies all official guidelines for intelligent NLP/AI chatbot architecture, Hugging Face Transformers integration, NLTK preprocessing, SQLite logging, and multi-turn context retention.

