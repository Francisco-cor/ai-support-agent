import aiosqlite, os
DB_PATH = os.getenv('RAG_DB', 'data/docs.db')

async def init_db():
    os.makedirs('data', exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute('CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY, title TEXT, content TEXT);')
        await db.execute('CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(content, content="documents", content_rowid="id");')
        await db.commit()

async def index_document(title, content):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('INSERT INTO documents (title, content) VALUES (?,?)', (title, content))
        rowid = cur.lastrowid
        await db.execute('INSERT INTO documents_fts(rowid, content) VALUES (?,?)', (rowid, content))
        await db.commit()
        return rowid

async def query_similar(query, limit=5):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('SELECT d.id, d.title, d.content FROM documents d JOIN documents_fts f ON d.id = f.rowid WHERE documents_fts MATCH ? LIMIT ?', (query, limit))
        rows = await cur.fetchall()
        return [{'id': r[0], 'title': r[1], 'content': r[2]} for r in rows]

async def list_documents(limit=20):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('SELECT id, title FROM documents ORDER BY id DESC LIMIT ?', (limit,))
        rows = await cur.fetchall()
        return [{'id': r[0], 'title': r[1]} for r in rows]
