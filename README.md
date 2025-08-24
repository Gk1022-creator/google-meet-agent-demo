# Google Meet Agent Demo

This project automates **Google Meet transcription, summarization, and Retrieval-Augmented Generation (RAG)** workflows.  
It is divided into **two main parts**:

---

## 📌 Part 1: Google Meet Bot

The Google Meet automation bot performs the following tasks:
- Automatically joins a Google Meet meeting via Chrome.
- Captures audio using **VB-Cable**.
- Transcribes meeting audio into text using **Faster-Whisper**.
- Saves both the **raw audio** and **transcribed text** into `meeting_logs/`.
- Summarizes the transcript into structured meeting notes.

### 🔧 Components
1. **`join_meet.py`** → Joins the Google Meet using Playwright.  
2. **`capture_transcribe.py`** → Captures meeting audio via VB-Cable and transcribes it.  
3. **`notes_worker.py`** → Summarizes the transcript into concise notes.  

---

## 📌 Part 2: RAG (Retrieval-Augmented Generation)

This module enables intelligent question answering and document retrieval.

- Supports **embedding creation** from:
  - JSON datasets (e.g., MiSed dataset of meetings)
  - PDF files
  - Word documents
- Indexing is handled by **Qdrant (vector database)**.
- Supports semantic **retrieval** based on user queries.
- Can be extended with **LLM tools and agents** for advanced capabilities.
- Uses **Ollama** for running embeddings and text generation locally.

---