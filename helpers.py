"""
Analytics and insights module for Reflect journaling app
Provides business logic for weekly analysis, emotional scoring, and reflections

AI USAGE DISCLOSURE (per CS50 requirements):
- Claude: Verified emotional scoring formula for statistical soundness
- All algorithms and reflections generation are original
- See CS50_REQUIREMENTS.md for detailed AI usage breakdown
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from database import get_entries_in_range, get_entries_for_user, get_conn


def compute_weekly_averages(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not entries:
        return {'mood': None, 'energy': None, 'anxiety': None, 'count': 0}
    moods = [e['mood'] for e in entries]
    energy = [e['energy'] for e in entries]
    anxiety = [e['anxiety'] for e in entries]
    return {
        'mood': round(sum(moods) / len(moods), 2),
        'energy': round(sum(energy) / len(energy), 2),
        'anxiety': round(sum(anxiety) / len(anxiety), 2),
        'count': len(entries)
    }


def compute_emotional_score(entry: Dict[str, Any]) -> float:
    # composite score: higher is better
    # weight mood 0.6, energy 0.3, anxiety -0.1
    score = entry['mood'] * 0.6 + entry['energy'] * 0.3 - entry['anxiety'] * 0.1
    return round(score, 2)


def generate_weekly_reflection(entries: List[Dict[str, Any]], user_id: int, db_path: str) -> str:
    # Current week
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=6)
    prev_start = week_start - timedelta(days=7)
    prev_end = week_start - timedelta(days=1)
    current = get_entries_in_range(db_path, user_id, week_start.isoformat(), today.isoformat())
    previous = get_entries_in_range(db_path, user_id, prev_start.isoformat(), prev_end.isoformat())
    cur_avg = compute_weekly_averages(current)
    prev_avg = compute_weekly_averages(previous)
    parts = []
    if cur_avg['count'] == 0:
        parts.append("You didn't log any entries this week. Try adding brief daily reflections to track patterns.")
        return '\n'.join(parts)
    parts.append(f"This week your average mood was {cur_avg['mood']}, energy {cur_avg['energy']}, anxiety {cur_avg['anxiety']}.")
    if prev_avg['count'] > 0 and cur_avg['mood'] is not None and prev_avg['mood'] is not None:
        diff = round(cur_avg['mood'] - prev_avg['mood'], 2)
        if diff > 0.2:
            parts.append(f"Your mood improved by {diff} compared to last week.")
        elif diff < -0.2:
            parts.append(f"Your mood decreased by {abs(diff)} compared to last week.")
        else:
            parts.append("Your mood was similar to last week.")
    parts.append(f"You logged reflections on {cur_avg['count']} day(s) this week.")
    # detect most frequent tag
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('''
    SELECT t.name, COUNT(*) as freq FROM tags t
    JOIN entry_tags et ON et.tag_id = t.id
    JOIN entries e ON e.id = et.entry_id
    WHERE e.user_id = ? AND e.date BETWEEN ? AND ?
    GROUP BY t.id ORDER BY freq DESC LIMIT 1
    ''', (user_id, week_start.isoformat(), today.isoformat()))
    row = c.fetchone()
    conn.close()
    if row:
        parts.append(f"{row['name'].capitalize()}-related events were the most common this week.")
    return ' '.join(parts)


def compute_streak(db_path: str, user_id: int) -> int:
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('SELECT DISTINCT date FROM entries WHERE user_id = ? ORDER BY date DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return 0
    streak = 0
    expected = None
    for r in rows:
        d = datetime.fromisoformat(r['date']).date()
        if expected is None:
            expected = d
        if d == expected:
            streak += 1
            expected = expected - timedelta(days=1)
        else:
            break
    return streak


def tag_correlation(db_path: str, user_id: int, start_date: str, end_date: str):
    # Return average mood per tag to see which tags associate with lower mood
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute('''
    SELECT t.name, AVG(e.mood) as avg_mood, COUNT(*) as cnt FROM tags t
    JOIN entry_tags et ON et.tag_id = t.id
    JOIN entries e ON e.id = et.entry_id
    WHERE e.user_id = ? AND e.date BETWEEN ? AND ?
    GROUP BY t.id ORDER BY avg_mood ASC
    ''', (user_id, start_date, end_date))
    rows = c.fetchall()
    conn.close()
    return rows
