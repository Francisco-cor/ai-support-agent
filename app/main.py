from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os, time
from .db import init_db, query_similar, index_document, list_documents
from .llm import query_llm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'changeme_secret')
DEFAULT_SYSTEM_PROMPT = os.getenv('DEFAULT_SYSTEM_PROMPT', 
    "You are a helpful technical support assistant. Your answers must be based strictly on the provided context. If the answer cannot be found in the context, explicitly state that you don't know."
)

app = FastAPI(title='Internal AI Support Agent (Gemini RAG)')

# Ensure static directory exists to prevent startup errors
os.makedirs("static", exist_ok=True)

# Mount the static directory to serve CSS/JS/HTML if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Pydantic Models ---

class ChatRequest(BaseModel):
    query: str

class IndexDoc(BaseModel):
    title: str
    content: str

# --- Lifecycle Events ---

@app.on_event('startup')
async def startup():
    """Initialize the database on server startup."""
    await init_db()

# --- Endpoints ---

@app.get("/")
async def read_root():
    """Serves the Chat UI."""
    # We assume index.html will be placed in 'static/' in Commit 6
    if os.path.exists("static/index.html"):
        return FileResponse('static/index.html')
    return {"message": "API is running. UI not found in static/index.html yet."}

@app.post('/api/chat')
async def chat(req: ChatRequest):
    """
    Core RAG Endpoint:
    1. Receive query.
    2. Search DB for similar docs (Retrieval).
    3. Send Query + Docs to Gemini (Generation).
    """
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail='Empty query')

    # 1. Retrieval: Get top 3 relevant documents
    docs = await query_similar(req.query, limit=3)
    
    # 2. Context Construction
    if not docs:
        # If no docs found, we pass an empty context indicator.
        # The System Prompt is responsible for saying "I don't know" in this case.
        context = "No relevant internal documents found."
    else:
        # Format: "--- Source: Title ---\nContent..."
        context = '\n\n'.join([f"--- Source: {d['title']} ---\n{d['content']}" for d in docs])

    # 3. Generation: Call LLM
    answer = await query_llm(
        system_instruction=DEFAULT_SYSTEM_PROMPT,
        user_query=req.query,
        context_text=context
    )

    # Return response with sources for traceability
    return {
        'answer': answer, 
        'sources': docs,
        'model': os.getenv('LLM_MODEL', 'gemini')
    }

@app.post('/api/docs/index')
async def index_doc(doc: IndexDoc, request: Request):
    """
    Endpoint to ingest new documents.
    Protected by a simple Secret Header.
    """
    secret = request.headers.get('X-WEBHOOK-SECRET') or request.query_params.get('secret')
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail='Invalid secret')
        
    rowid = await index_document(doc.title, doc.content)
    return {'ok': True, 'id': rowid}

@app.get('/api/docs/list')
async def docs_list():
    """Helper to see what's inside the DB."""
    items = await list_documents()
    return {'items': items}

@app.get('/health')
async def health():
    """Health check for monitoring."""
    return {
        'status': 'ok', 
        'provider': 'Google Gemini', 
        'ts': time.time()
    }