
import requests
from .config import settings

class OllamaLLM:
    def __init__(self, base_url: str = None, model: str = None):
        self.base = base_url or settings.ollama_url
        self.base = "http://localhost:11434"
        self.model = "llama3"

    def generate(self, prompt: str, timeout: int = 300):
        print(self.model, prompt)
        body = {"model": self.model, "prompt": prompt, "max_tokens": 512, "temperature": 0.2, "stream": False}
        r = requests.post(f"{self.base}/api/generate", json=body, timeout=timeout)
        r.raise_for_status()
        return r.json()

    def simple_text(self, prompt: str, timeout: int = 300) -> str:
        resp = self.generate(prompt, timeout=timeout)
        if isinstance(resp, dict):
            if "text" in resp:
                return resp["text"]
            if "generation" in resp:
                gen = resp["generation"]
                if isinstance(gen, str):
                    return gen
                if isinstance(gen, list) and gen:
                    first = gen[0]
                    if isinstance(first, dict):
                        return first.get("content") or str(first)
                    return str(first)
        return str(resp)

class OpenAILLM:
    def __init__(self, model: str = "gpt-4o-mini", api_key: str = None):
        import openai
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.api_key)

    def simple_text(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512
        )
        return resp.choices[0].message.content