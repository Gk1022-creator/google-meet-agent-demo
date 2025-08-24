
# Backend - Meeting Agent with Tools

This backend exposes:
- POST /chat       -> non-streaming chat (JSON)
- POST /chat/stream -> SSE streaming of responses

Requirements:
- Qdrant and Ollama running (or adjust .env)
- python -m pip install -r requirements.txt
- run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
