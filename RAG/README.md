
# React Agent Project (Backend + Frontend)

This project contains:
- backend/: FastAPI agent backend with tool-calling (Qdrant retrieval)
- frontend/: React (Vite) chat UI

Quick start:
1. Ensure Docker is installed.
2. Start qdrant: `docker compose up -d qdrant`
3. Start Ollama on host (or adjust OLLAMA_URL in backend/.env)
4. Build & run backend: `docker compose up -d backend` or run locally with uvicorn
5. Start frontend: `cd frontend && npm install && npm run dev` (set proxy to backend or set window.__BACKEND__ in browser)
