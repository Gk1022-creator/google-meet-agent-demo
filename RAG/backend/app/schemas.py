
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ChatRequest(BaseModel):
    query: str
    use_retrieval: bool = True
    max_context_items: Optional[int] = None

class ToolCall(BaseModel):
    name: str
    args: Dict[str, Any]

class ChatResponse(BaseModel):
    text: str
    retrieved: List[Dict] = []
