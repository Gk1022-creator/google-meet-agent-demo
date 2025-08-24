
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from .schemas import ChatRequest
from .agent import run_agent
import asyncio
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Meeting Agent with Tools")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # your frontend port
    allow_credentials=True,
    allow_methods=["*"],   # allow POST, GET, OPTIONS, etc
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(req: ChatRequest):
    res = run_agent(req.query, use_retrieval=req.use_retrieval, max_context_items=req.max_context_items)
    return JSONResponse(content=res)

@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    req = ChatRequest(**body)
    async def event_gen():
        res = run_agent(req.query, use_retrieval=req.use_retrieval, max_context_items=req.max_context_items)
        text = res.get('text') or ''
        chunk_size = 200
        for i in range(0, len(text), chunk_size):
            yield {"event":"message","data": text[i:i+chunk_size]}
            await asyncio.sleep(settings.sse_chunk_delay)
        yield {"event":"retrieved","data": str(res.get('retrieved', []))}
    return EventSourceResponse(event_gen())
