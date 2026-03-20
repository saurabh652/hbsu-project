import sqlite3

conn = sqlite3.connect("content.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS content (
    program TEXT,
    subject TEXT,
    unit TEXT,
    content TEXT,
    PRIMARY KEY (program, subject, unit)
)
""")
conn.commit()

def get_content(program, subject, unit):
    cur.execute(
        "SELECT content FROM content WHERE program=? AND subject=? AND unit=?",
        (program, subject, unit)
    )
    row = cur.fetchone()
    return row[0] if row else None

def save_content(program, subject, unit, content):
    cur.execute(
        "INSERT OR REPLACE INTO content VALUES (?,?,?,?)",
        (program, subject, unit, content)
    )
    conn.commit()
