import sqlite3

conn = sqlite3.connect("finance.db", check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password BLOB
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions(
        username TEXT,
        month TEXT,
        desc TEXT,
        amt REAL,
        cat TEXT
    )
    """)
    conn.commit()