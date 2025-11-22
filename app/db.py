import aiosqlite
import os

# DB configuration
DB_PATH = os.getenv('RAG_DB', 'data/docs.db')

async def init_db():
    """Initializes the SQLite database with FTS5 support and sync triggers."""
    os.makedirs('data', exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        # Enable Write-Ahead Logging for better concurrency
        await db.execute("PRAGMA journal_mode=WAL;")
        
        # 1. Standard storage table (The Source of Truth)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS documents(
                id INTEGER PRIMARY KEY, 
                title TEXT, 
                content TEXT
            );
        ''')
        
        # 2. Full Text Search (FTS5) virtual table
        # We link it to the main table using content="documents" to minimize storage overhead
        await db.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts 
            USING fts5(content, title, content="documents", content_rowid="id");
        ''')
        
        # 3. Trigger: Automatically update FTS index when a new doc is inserted
        await db.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
              INSERT INTO documents_fts(rowid, content, title) VALUES (new.id, new.content, new.title);
            END;
        ''')
        
        # (Optional) We could add triggers for DELETE and UPDATE here for a full production system
        
        await db.commit()

async def index_document(title, content):
    """Inserts a document into the DB. The Trigger handles the FTS indexing."""
    async with aiosqlite.connect(DB_PATH) as db:
        # We only insert into the main table. The Trigger does the rest.
        cur = await db.execute('INSERT INTO documents (title, content) VALUES (?,?)', (title, content))
        await db.commit()
        return cur.lastrowid

async def query_similar(query_text, limit=5):
    """
    Performs a full-text search using FTS5.
    Includes basic sanitization to prevent syntax errors in FTS queries.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Sanitize: simple approach, remove quotes that might break FTS syntax
        # Example: if user types ' "error" ', SQLite FTS might expect a specific phrase logic.
        # We strip them to keep the demo robust.
        clean_query = query_text.replace('"', '').replace("'", "")
        
        # We join FTS table with the main table to get the clean data
        # "rank" is a hidden column in FTS5 used for relevance sorting
        sql = '''
            SELECT d.id, d.title, d.content 
            FROM documents d 
            JOIN documents_fts f ON d.id = f.rowid 
            WHERE documents_fts MATCH ? 
            ORDER BY rank 
            LIMIT ?
        '''
        
        try:
            # We use double quotes around the parameter inside the query logic implicitly by FTS 
            # or pass the raw string. FTS MATCH expects a string syntax.
            cur = await db.execute(sql, (clean_query, limit))
            rows = await cur.fetchall()
        except Exception as e:
            # Fallback if query is malformed (e.g. boolean operators misuse)
            print(f"Search error: {e}")
            return []

        return [{'id': r[0], 'title': r[1], 'content': r[2]} for r in rows]

async def list_documents(limit=20):
    """Returns the most recent documents indexed."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute('SELECT id, title FROM documents ORDER BY id DESC LIMIT ?', (limit,))
        rows = await cur.fetchall()
        return [{'id': r[0], 'title': r[1]} for r in rows]