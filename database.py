import sqlite3

DB_NAME = "url_shortener.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE NOT NULL,
                long_url TEXT NOT NULL
            );
        """)
        conn.commit()

def insert_url(short_code, long_url):
    with get_connection() as conn:
        conn.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
        conn.commit()

def get_long_url(short_code):
    with get_connection() as conn:
        row = conn.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,)).fetchone()
        return row["long_url"] if row else None
