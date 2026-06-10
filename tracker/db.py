import sqlite3

DB_PATH = "jobs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            company      TEXT,
            role         TEXT,
            url          TEXT UNIQUE,
            score        INTEGER,
            status       TEXT DEFAULT 'pending_review',
            applied_at   TIMESTAMP,
            resume_path  TEXT,
            notes        TEXT,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def is_duplicate(conn, url):
    row = conn.execute(
        "SELECT id FROM applications WHERE url = ?", (url,)
    ).fetchone()
    return row is not None

def log_application(conn, company, role, url, score, resume_path):
    conn.execute("""
        INSERT OR IGNORE INTO applications
        (company, role, url, score, resume_path)
        VALUES (?, ?, ?, ?, ?)
    """, (company, role, url, score, resume_path))
    conn.commit()

def get_all_applications(conn):
    return conn.execute("""
        SELECT company, role, score, status, created_at
        FROM applications
        ORDER BY created_at DESC
    """).fetchall()