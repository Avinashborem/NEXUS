# core/memory.py — Persistent Memory (SQLite)
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nexus_memory.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Conversation history
    c.execute('''CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )''')
    # Long term facts about the user
    c.execute('''CREATE TABLE IF NOT EXISTS user_facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT NOT NULL,
        updated TEXT NOT NULL
    )''')
    # Frequently used apps/commands
    c.execute('''CREATE TABLE IF NOT EXISTS usage_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command TEXT NOT NULL,
        count INTEGER DEFAULT 1,
        last_used TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def save_message(role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO conversations (role, content, timestamp) VALUES (?, ?, ?)",
              (role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_recent_history(limit=20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def save_user_fact(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO user_facts (key, value, updated)
                 VALUES (?, ?, ?)
                 ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated=excluded.updated''',
              (key, value, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_facts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT key, value FROM user_facts")
    rows = c.fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}

def track_command(command):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, count FROM usage_stats WHERE command=?", (command,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE usage_stats SET count=?, last_used=? WHERE id=?",
                  (row[1]+1, datetime.now().isoformat(), row[0]))
    else:
        c.execute("INSERT INTO usage_stats (command, count, last_used) VALUES (?, 1, ?)",
                  (command, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_memory_summary():
    facts = get_user_facts()
    if not facts:
        return ""
    lines = [f"{k}: {v}" for k, v in facts.items()]
    return "What I know about you:\n" + "\n".join(lines)

# Initialize on import
init_db()