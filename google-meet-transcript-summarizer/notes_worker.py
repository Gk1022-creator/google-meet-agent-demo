import requests
import os
import math
from dotenv import load_dotenv
load_dotenv()


OPENAI_KEY = os.getenv("OPENAI_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")  # default local Ollama
MAX_TOKENS = 3000  # safe window size (adjust per model)


def chunk_text(text: str, max_len: int = MAX_TOKENS) -> list[str]:
    """
    Roughly split text into chunks that fit model context.
    Uses whitespace split, not perfect but avoids exceeding context.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_len):
        chunk = " ".join(words[i:i+max_len])
        chunks.append(chunk)
    return chunks


def summarize_openai(text: str) -> str:
    """Summarize with OpenAI API"""
    prompt = f"Turn these meeting utterances into a short summary, list decisions and action items:\n\n{text}"

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 512
        },
        timeout=120
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def summarize_ollama(text: str) -> str:
    """Summarize with local Ollama Llama3 model"""
    prompt = f"Turn these meeting utterances into a short summary, list decisions and action items:\n\n{text}"

    r = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": "llama3", "prompt": prompt,"max_tokens": 512, "temperature": 0.2, "stream": False},
        timeout=300
    )
    r.raise_for_status()
    data = r.json()
    return data.get("response", "")


def summarize_chunk(text: str) -> str:
    """Auto choose OpenAI or Ollama + handle long text"""
    chunks = chunk_text(text, MAX_TOKENS)
    summaries = []

    for ch in chunks:
        try:
            if OPENAI_KEY:  # Try OpenAI first
                summaries.append(summarize_openai(ch))
            else:  # Fall back to Ollama
                summaries.append(summarize_ollama(ch))
        except Exception as e:
            print("⚠️ Falling back to Ollama:", e)
            summaries.append(summarize_ollama(ch))

    # Merge all chunk summaries into final summary
    final_text = "\n".join(summaries)
    if len(summaries) > 1:
        # If multiple chunks → summarize again for a clean final note
        try:
            if OPENAI_KEY:
                return summarize_openai(final_text)
            else:
                return summarize_ollama(final_text)
        except Exception as e:
            print("⚠️ Error in final summarization, returning raw summaries", e)
            return final_text
    else:
        return final_text


# Example usage:
if __name__ == "__main__":

    filepath = os.environ.get("FILE_PATH")
    with open(filepath, "r") as f:
      transcript_window = f.read()
    # transcript_window = "Mm hmm yeah so next steps are to migrate database, finalize UI design and prepare launch plan..."
    summary = summarize_chunk(transcript_window)
    print("🔹 SUMMARY:\n", summary)
