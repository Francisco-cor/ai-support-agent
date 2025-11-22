from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os, time
from .db import init_db, query_similar, index_document, list_documents
from .llm import query_llm
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'changeme_secret')

app = FastAPI(title='Inzend — AI Support Agent (RAG)')

class ChatRequest(BaseModel):
    user_id: str | None = None
    query: str

class IndexDoc(BaseModel):
    title: str
    content: str

@app.on_event('startup')
async def startup():
    await init_db()

@app.post('/chat')
async def chat(req: ChatRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail='Empty query')

    docs = await query_similar(req.query, limit=4)
    context = '\n\n'.join([f"Title: {d['title']}\n{d['content']}" for d in docs])
    messages = [
        {'role':'system','content': os.getenv('DEFAULT_SYSTEM_PROMPT','You are a helpful support assistant.')},
        {'role':'user','content': f"Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {req.query}"}
    ]
    answer = await query_llm(messages)
    return {'answer': answer, 'sources': docs}

@app.post('/docs/index')
async def index_doc(doc: IndexDoc, request: Request):
    secret = request.headers.get('X-WEBHOOK-SECRET') or request.query_params.get('secret')
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail='Invalid secret')
    rowid = await index_document(doc.title, doc.content)
    return {'ok': True, 'id': rowid}

@app.get('/docs/list')
async def docs_list():
    items = await list_documents()
    return {'items': items}

@app.get('/health')
async def health():
    return {'status': 'ok', 'ts': time.time()}
