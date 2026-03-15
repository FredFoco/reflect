"""
Seed data generator for Reflect journaling app
Creates idempotent test data for development and testing

Features:
- Incremental generation (only adds missing entries)
- Clean mode (deletes and recreates user)
- Batch database operations for performance
- Progress reporting every 50 entries

Usage:
  python3 seeds.py           # Add missing entries
  python3 seeds.py --clean   # Reset everything

AI USAGE DISCLOSURE (per CS50 requirements):
- GitHub Copilot: Suggested basic loop and data generation patterns
- Database integration, idempotency, and batch operations are original
- See CS50_REQUIREMENTS.md for detailed AI usage breakdown
"""

import os
import random
import sqlite3
from datetime import datetime, timedelta, timezone

from database import init_db, create_user, get_user_by_username, create_entry, set_entry_tags, get_conn, delete_user_and_entries

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'reflect.db')


def count_user_entries(user_id):
    """Count how many entries exist for this user."""
    conn = get_conn(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as cnt FROM entries WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row['cnt'] if row else 0


def seed(clean=False):
    init_db(DB_PATH)
    username = 'teste'
    password = 'teste'
    
    # If clean flag, delete existing user and start fresh
    if clean:
        if delete_user_and_entries(DB_PATH, username):
            print(f'✓ Deleted existing user {username}')
    
    # Try to get user, if not exists create it
    user = get_user_by_username(DB_PATH, username)
    if user:
        print(f'✓ User {username} exists')
        user_id = user['id']
    else:
        try:
            create_user(DB_PATH, username, password)
            user = get_user_by_username(DB_PATH, username)
            user_id = user['id']
            print(f'✓ Created user {username}')
        except Exception as e:
            print(f'✗ Failed to create user: {e}')
            return

    # Check how many entries exist
    existing_count = count_user_entries(user_id)
    target_count = 365
    needed = target_count - existing_count
    
    if needed <= 0:
        print(f'✓ User already has {existing_count} entries. Target is {target_count}. Done.')
        return
    
    print(f'✓ User has {existing_count} entries. Creating {needed} more to reach {target_count}...')

    tags_pool = ['work', 'relationship', 'health', 'family', 'social', 'rest', 'exercise', 'study', 'travel', 'finance']
    today = datetime.now(timezone.utc).date()
    descriptions = [
        'Had a productive day and got a lot done.',
        'Felt a bit overwhelmed with tasks.',
        'Spent time with family and felt supported.',
        'Went for a walk and felt calmer.',
        'Had a stressful meeting at work.',
        'Relaxed and read a book in the evening.',
        'Socialized with friends, enjoyable night.',
        'Skipped exercise and noticed lower energy.',
        'Focused study session felt rewarding.',
        'Financial worries popped up today.'
    ]

    # Create entries from (today - target_count) backwards, but skip ones that already exist
    created = 0
    for i in range(target_count):
        d = today - timedelta(days=i)
        # Check if entry for this date already exists
        conn = get_conn(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM entries WHERE user_id = ? AND date = ?', (user_id, d.isoformat()))
        exists = c.fetchone()
        conn.close()
        
        if exists:
            continue  # Skip if already exists
        
        mood = random.randint(0, 10)
        energy = random.randint(0, 10)
        anxiety = random.randint(0, 10)
        desc = random.choice(descriptions)
        entry_id = create_entry(DB_PATH, user_id, d.isoformat(), mood, energy, anxiety, desc)
        chosen = random.sample(tags_pool, k=random.randint(0, 3))
        set_entry_tags(DB_PATH, entry_id, chosen)
        created += 1
        
        if created % 50 == 0:
            print(f'  ✓ {created} new entries created')

    print(f'✓ Done. Total entries for {username}: {existing_count + created}')


if __name__ == '__main__':
    import sys
    clean = '--clean' in sys.argv
    seed(clean=clean)
