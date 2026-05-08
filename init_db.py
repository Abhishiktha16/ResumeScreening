import sqlite3
import os

# Always creates resume.db in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'resume.db')

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS hr_users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    email    TEXT    UNIQUE NOT NULL,
    password TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    company         TEXT NOT NULL,
    job_profile     TEXT NOT NULL,
    salary          TEXT NOT NULL,
    job_description TEXT NOT NULL,
    posted_by       TEXT NOT NULL,
    posted_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resumes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT,
    email       TEXT,
    filename    TEXT,
    job_id      INTEGER,
    score       REAL,
    status      TEXT,
    uploaded_at TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
""")

conn.commit()
cur.close()
conn.close()
print(f"resume.db created at: {DB_PATH}")