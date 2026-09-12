# Codec Support AI

### AI-Powered Customer Support & FAQ Chatbot

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![NLP](https://img.shields.io/badge/NLP-NLTK-154F5C)](https://www.nltk.org/)
[![Transformers](https://img.shields.io/badge/AI-Transformers-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tests](https://img.shields.io/badge/Tests-14%20Passing-success)](https://pytest.org/)
[![Deployment](https://img.shields.io/badge/Deployment-Render-46E3B7)](https://render.com/)

> A context-aware AI customer support chatbot built with Python, NLP, Transformer-based semantic matching, Flask, and SQLite.

**Live Demo:**  
https://codec-ai-support.onrender.com

**GitHub Repository:**  
https://github.com/Sai-Dharla/Codec_Ai_Support

---

## Overview

**Codec Support AI** is an AI-powered customer support and FAQ chatbot designed to understand user questions, identify their intent, provide relevant responses, and maintain conversation context across multiple turns.

Unlike a basic keyword or rule-based chatbot, the application combines **Natural Language Processing (NLP)** with **Transformer-based semantic embeddings** to match user questions with relevant FAQ knowledge.

The chatbot also maintains session context, allowing it to understand follow-up questions that depend on previous messages.

For example:

> **User:** How can I reset my password?

> **Bot:** Provides password-reset instructions.

> **User:** What if I don't receive the email?

The chatbot can interpret **"the email"** in the context of the previous password-reset conversation.

---

## Internship Context

This project was developed as part of my **Python Developer Internship at Codec Technologies**.

The project focuses on practical Python development, NLP integration, backend API development, database integration, automated testing, and cloud deployment.

---

## Key Features

- Context-aware multi-turn conversations
- Natural Language Processing using NLTK
- Transformer-based semantic matching
- FAQ knowledge-base integration
- Session and conversation management
- Confidence-based response handling
- Graceful fallback for unclear queries
- SQLite-based interaction logging
- REST API for chatbot communication
- Responsive web-based chat interface
- Quick customer-support prompts
- Password-reset support
- Order-related support
- Refund-related support
- Payment-related support
- Automated unit and integration testing
- Production deployment with Gunicorn
- CPU-oriented Transformer model configuration

---

## How It Works

The chatbot follows a modular processing pipeline:

```text
                    User Question
                         │
                         ▼
              ┌─────────────────────┐
              │   Web Chat Interface │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │     Flask API       │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   NLTK Processing   │
              │ Tokenization / NLP  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Transformer Model   │
              │ Semantic Embedding  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Context Management  │
              │ Session / Follow-up │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Response Selection  │
              │ + Confidence Check  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │    SQLite Logging   │
              └──────────┬──────────┘
                         │
                         ▼
                  Response to User