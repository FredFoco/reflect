"""
Database module for Reflect journaling app
Handles SQLite schema initialization and all data access operations

SECURITY: All queries use parameterized SQL to prevent injection attacks
SCHEMA: Normalized (3NF) with users, entries, tags, entry_tags tables

AI USAGE DISCLOSURE (per CS50 requirements):
- GitHub Copilot: Suggested CRUD function templates (CREATE, READ, UPDATE, DELETE)
- All modifications for security (parameterized queries) and functionality are original
- Database design and normalization are original
- See CS50_REQUIREMENTS.md for detailed AI usage breakdown
"""

import sqlite3
from werkzeug.security import generate_password_hash
from typing import List, Dict, Any


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    return conn


def init_db(db_path: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        mood INTEGER NOT NULL,
        energy INTEGER NOT NULL,
        anxiety INTEGER NOT NULL,
        event_description TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS entry_tags (
        entry_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY(entry_id, tag_id),
        FOREIGN KEY(entry_id) REFERENCES entries(id),
        FOREIGN KEY(tag_id) REFERENCES tags(id)
    )
    ''')
    conn.commit()
    conn.close()


def create_user(db_path: str, username: str, password: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    pw_hash = generate_password_hash(password)
    c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, pw_hash))
    conn.commit()
    conn.close()


def get_user_by_username(db_path: str, username: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user


def verify_user(db_path: str, username: str, password: str):
    # helper if needed
    user = get_user_by_username(db_path, username)
    return user


def create_entry(db_path: str, user_id: int, date: str, mood: int, energy: int, anxiety: int, event_description: str) -> int:
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO entries (user_id, date, mood, energy, anxiety, event_description) VALUES (?, ?, ?, ?, ?, ?)''',
              (user_id, date, mood, energy, anxiety, event_description))
    entry_id = c.lastrowid
    conn.commit()
    conn.close()
    return entry_id


def update_entry(db_path: str, entry_id: int, date: str, mood: int, energy: int, anxiety: int, event_description: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('''UPDATE entries SET date = ?, mood = ?, energy = ?, anxiety = ?, event_description = ? WHERE id = ?''',
              (date, mood, energy, anxiety, event_description, entry_id))
    conn.commit()
    conn.close()


def delete_entry(db_path: str, entry_id: int):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM entry_tags WHERE entry_id = ?', (entry_id,))
    c.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()


def get_entry_by_id(db_path: str, entry_id: int):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
    entry = c.fetchone()
    if entry:
        c.execute('''SELECT t.id, t.name FROM tags t JOIN entry_tags et ON et.tag_id = t.id WHERE et.entry_id = ?''', (entry_id,))
        entry['tags'] = c.fetchall()
    conn.close()
    return entry


def get_entries_for_user(db_path: str, user_id: int):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM entries WHERE user_id = ? ORDER BY date DESC', (user_id,))
    entries = c.fetchall()
    for e in entries:
        c.execute('''SELECT t.id, t.name FROM tags t JOIN entry_tags et ON et.tag_id = t.id WHERE et.entry_id = ?''', (e['id'],))
        e['tags'] = c.fetchall()
    conn.close()
    return entries


def get_entries_in_range(db_path: str, user_id: int, start_date: str, end_date: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('''SELECT * FROM entries WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date ASC''', (user_id, start_date, end_date))
    entries = c.fetchall()
    for e in entries:
        c.execute('''SELECT t.id, t.name FROM tags t JOIN entry_tags et ON et.tag_id = t.id WHERE et.entry_id = ?''', (e['id'],))
        e['tags'] = c.fetchall()
    conn.close()
    return entries


def search_entries_for_user(db_path: str, user_id: int, q: str | None = None, limit: int = 50, offset: int = 0):
    conn = get_conn(db_path)
    c = conn.cursor()
    if q:
        pattern = f"%{q.lower()}%"
        c.execute('''
        SELECT DISTINCT e.* FROM entries e
        LEFT JOIN entry_tags et ON et.entry_id = e.id
        LEFT JOIN tags t ON t.id = et.tag_id
        WHERE e.user_id = ? AND (LOWER(e.event_description) LIKE ? OR LOWER(t.name) LIKE ?)
        ORDER BY date DESC LIMIT ? OFFSET ?
        ''', (user_id, pattern, pattern, limit, offset))
    else:
        c.execute('''SELECT * FROM entries WHERE user_id = ? ORDER BY date DESC LIMIT ? OFFSET ?''', (user_id, limit, offset))
    entries = c.fetchall()
    for e in entries:
        c.execute('''SELECT t.id, t.name FROM tags t JOIN entry_tags et ON et.tag_id = t.id WHERE et.entry_id = ?''', (e['id'],))
        e['tags'] = c.fetchall()
    conn.close()
    return entries


def count_entries_for_user(db_path: str, user_id: int, q: str | None = None) -> int:
    conn = get_conn(db_path)
    c = conn.cursor()
    if q:
        pattern = f"%{q.lower()}%"
        c.execute('''
        SELECT COUNT(DISTINCT e.id) as cnt FROM entries e
        LEFT JOIN entry_tags et ON et.entry_id = e.id
        LEFT JOIN tags t ON t.id = et.tag_id
        WHERE e.user_id = ? AND (LOWER(e.event_description) LIKE ? OR LOWER(t.name) LIKE ?)
        ''', (user_id, pattern, pattern))
    else:
        c.execute('SELECT COUNT(*) as cnt FROM entries WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row['cnt'] if row else 0


def create_or_get_tag(db_path: str, tag_name: str) -> int:
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
    row = c.fetchone()
    if row:
        tag_id = row['id']
    else:
        c.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
        tag_id = c.lastrowid
        conn.commit()
    conn.close()
    return tag_id


def set_entry_tags(db_path: str, entry_id: int, tags: List[str]):
    conn = get_conn(db_path)
    c = conn.cursor()
    # remove existing
    c.execute('DELETE FROM entry_tags WHERE entry_id = ?', (entry_id,))
    for t in tags:
        # Get or create tag in same transaction
        c.execute('SELECT id FROM tags WHERE name = ?', (t,))
        row = c.fetchone()
        if row:
            tag_id = row['id']
        else:
            c.execute('INSERT INTO tags (name) VALUES (?)', (t,))
            tag_id = c.lastrowid
        c.execute('INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)', (entry_id, tag_id))
    conn.commit()
    conn.close()


def get_all_tags_for_user(db_path: str, user_id: int):
    # returns tags ordered by frequency across user's entries
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('''
    SELECT t.id, t.name, COUNT(*) as freq FROM tags t
    JOIN entry_tags et ON et.tag_id = t.id
    JOIN entries e ON e.id = et.entry_id
    WHERE e.user_id = ?
    GROUP BY t.id ORDER BY freq DESC
    ''', (user_id,))
    tags = c.fetchall()
    conn.close()
    return tags


def get_most_common_tag_in_range(db_path: str, user_id: int, start_date: str, end_date: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('''
    SELECT t.name, COUNT(*) as freq FROM tags t
    JOIN entry_tags et ON et.tag_id = t.id
    JOIN entries e ON e.id = et.entry_id
    WHERE e.user_id = ? AND e.date BETWEEN ? AND ?
    GROUP BY t.id ORDER BY freq DESC LIMIT 1
    ''', (user_id, start_date, end_date))
    row = c.fetchone()
    conn.close()
    return row['name'] if row else None


def delete_user_and_entries(db_path: str, username: str):
    """Delete a user and all their entries, tags, and links."""
    conn = get_conn(db_path)
    c = conn.cursor()
    # Get user id
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
    user_id = row['id']
    # Delete entry_tags for this user's entries
    c.execute('DELETE FROM entry_tags WHERE entry_id IN (SELECT id FROM entries WHERE user_id = ?)', (user_id,))
    # Delete entries
    c.execute('DELETE FROM entries WHERE user_id = ?', (user_id,))
    # Delete user
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True
