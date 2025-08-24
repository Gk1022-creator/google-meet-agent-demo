import re, json
from typing import List, Dict, Any, Optional
from .embeddings import OllamaEmbedder, OpenAIEmbedder
from .llm import OllamaLLM, OpenAILLM
from .tools import TOOLS, search_qdrant
from .config import settings

# --- Choose backend depending on key ---
if getattr(settings, "openai_api_key", None):  # if key exists in config
    embedder = OpenAIEmbedder(api_key=settings.openai_api_key)
    llm = OpenAILLM(api_key=settings.openai_api_key)
else:
    embedder = OllamaEmbedder()
    llm = OllamaLLM()


PROMPT_SYSTEM = """You are MeetingAgent.
When answering, provide a concise, actionable answer and list explicit action items if relevant."""

PROMPT_USER = """CONTEXT:
{context}

QUESTION:
{question}

Strictly use context data and return answer based on that on more concise and readable way.

"""
# If you call a tool, use the exact token: CALL_TOOL(name,args_json)
# Example: CALL_TOOL(qdrant.search, {{"query":"budget", "top_k":5}})
# Otherwise reply with ANSWER: <your answer>


def prepare_context(hits: List[Dict[str,Any]], max_items: Optional[int] = None) -> str:
    items = hits[: (max_items or settings.top_k)]
    blocks = []
    for h in items:
        p = h.get("payload", {})
        text = p.get("text") or p.get("excerpt") or ""
        title = p.get("title") or p.get("origin_id") or "(doc)"
        blocks.append(text)
        # blocks.append(f"-- {title} (score={h['score']:.3f})\n{text[:800]}")
    return "\n\n".join(blocks)


def run_agent(query: str, use_retrieval: bool = True, max_context_items: Optional[int] = None) -> Dict[str,Any]:
    """Run a react-style agent with optional retrieval."""

    context = "(no context)"
    retrieved = []

    while True:
        # Ask model what to do
        prompt = PROMPT_SYSTEM + "\n\n" + PROMPT_USER.format(context=context, question=query)
        decision = (llm.simple_text(prompt) or "").strip()

        # --- Tool Call ---
        if decision.startswith("CALL_TOOL"):
            m = re.search(r'CALL_TOOL\(([^,]+)\s*,\s*(\{.*\})\)', decision)
            if not m:
                return {"text": "Agent error: malformed CALL_TOOL", "retrieved": retrieved}

            tool_name = m.group(1).strip()
            try:
                args = json.loads(m.group(2))
            except Exception:
                args = {}

            tool = TOOLS.get(tool_name)
            tool_output = None
            if tool:
                if tool_name == "qdrant.search" and "query" in args:
                    qvec = embedder.embed([args["query"]])[0]
                    top_k = args.get("top_k") or settings.top_k
                    hits = tool(qvec, top_k=top_k)
                    tool_output = hits
                    retrieved = hits
                else:
                    tool_output = tool(**args)

            # Inject tool output back to model
            context = f"TOOL_OUTPUT({tool_name},{json.dumps(tool_output)})"
            continue  # loop again → model sees updated context

        # --- Direct Answer ---
        elif decision.startswith("ANSWER:"):
            return {"text": decision.replace("ANSWER:", "").strip(), "retrieved": retrieved}

        # --- No tool requested, but retrieval is allowed ---
        else:
            if use_retrieval:
                qvec = embedder.embed([query])
                hits = search_qdrant(qvec, top_k=(max_context_items or settings.top_k))
                retrieved = hits
                ctx = prepare_context(hits, max_context_items)
                # re-ask model with retrieval context
                context = ctx
                use_retrieval = False  # prevent infinite loop
                continue
            else:
                import ast
                data = ast.literal_eval(decision)
                return {"text": data["response"], "retrieved": retrieved}
