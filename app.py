"""
Reflect - Structured Journaling and Emotional Self-Tracking App
CS50 Final Project

This module implements the Flask application, routes, and Jinja filters.

AI USAGE DISCLOSURE (per CS50 requirements):
- GitHub Copilot: Used for routine Flask routing templates (GET/POST handlers)
- All core algorithms, security measures, and feature integration are original
- See CS50_REQUIREMENTS.md for detailed AI usage breakdown
"""

from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta

from database import (
    init_db,
    create_user,
    get_user_by_username,
    create_entry,
    get_entries_for_user,
    get_entry_by_id,
    update_entry,
    delete_entry,
    get_entries_in_range,
    get_all_tags_for_user,
    set_entry_tags,
    get_most_common_tag_in_range,
    search_entries_for_user,
    count_entries_for_user,
)
from helpers import (
    generate_weekly_reflection,
    compute_weekly_averages,
    compute_streak,
    compute_emotional_score,
    tag_correlation,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'reflect.db')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('REFLECT_SECRET', 'dev-secret-change-me')


# Initialize the database at import time to avoid relying on decorators
# which may vary across Flask versions.
init_db(DATABASE_PATH)


def login_required(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return wrapper


@app.route('/')
def index():
    if 'user_id' in session:
        # Show new entry form on the homepage for quick journaling
        tags = get_all_tags_for_user(DATABASE_PATH, session.get('user_id'))
        default_date = datetime.utcnow().date().isoformat()
        return render_template('new_entry.html', tags=tags, default_date=default_date)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Username and password required')
            return render_template('register.html')
        try:
            create_user(DATABASE_PATH, username, password)
        except sqlite3.IntegrityError:
            flash('Username already exists')
            return render_template('register.html')
        flash('Account created. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = get_user_by_username(DATABASE_PATH, username)
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=6)
    entries = get_entries_in_range(DATABASE_PATH, user_id, week_start.isoformat(), today.isoformat())
    averages = compute_weekly_averages(entries)
    streak = compute_streak(DATABASE_PATH, user_id)
    most_common_tag = get_most_common_tag_in_range(DATABASE_PATH, user_id, week_start.isoformat(), today.isoformat())
    labels = [e['date'] for e in entries]
    moods = [e['mood'] for e in entries]
    energy = [e['energy'] for e in entries]
    anxiety = [e['anxiety'] for e in entries]
    return render_template('dashboard.html', averages=averages, streak=streak, labels=labels, moods=moods, energy=energy, anxiety=anxiety, most_common_tag=most_common_tag, entries=entries)


@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    if request.method == 'POST':
        user_id = session['user_id']
        date = request.form.get('date') or datetime.utcnow().date().isoformat()
        mood = int(request.form.get('mood', 5))
        energy = int(request.form.get('energy', 5))
        anxiety = int(request.form.get('anxiety', 5))
        event_description = request.form.get('event_description', '')
        tags_text = request.form.get('tags', '')
        entry_id = create_entry(DATABASE_PATH, user_id, date, mood, energy, anxiety, event_description)
        tags = [t.strip().lower() for t in tags_text.split(',') if t.strip()]
        set_entry_tags(DATABASE_PATH, entry_id, tags)
        return redirect(url_for('dashboard'))
    tags = get_all_tags_for_user(DATABASE_PATH, session.get('user_id'))
    return render_template('new_entry.html', tags=tags)


@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry_route(entry_id):
    user_id = session['user_id']
    entry = get_entry_by_id(DATABASE_PATH, entry_id)
    if not entry or entry['user_id'] != user_id:
        flash('Entry not found')
        return redirect(url_for('history'))
    if request.method == 'POST':
        date = request.form.get('date')
        mood = int(request.form.get('mood', 5))
        energy = int(request.form.get('energy', 5))
        anxiety = int(request.form.get('anxiety', 5))
        event_description = request.form.get('event_description', '')
        tags_text = request.form.get('tags', '')
        update_entry(DATABASE_PATH, entry_id, date, mood, energy, anxiety, event_description)
        tags = [t.strip().lower() for t in tags_text.split(',') if t.strip()]
        set_entry_tags(DATABASE_PATH, entry_id, tags)
        return redirect(url_for('history'))
    tags = ', '.join([t['name'] for t in get_all_tags_for_user(DATABASE_PATH, user_id)])
    return render_template('edit_entry.html', entry=entry, tags=tags)


@app.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry_route(entry_id):
    user_id = session['user_id']
    entry = get_entry_by_id(DATABASE_PATH, entry_id)
    if entry and entry['user_id'] == user_id:
        delete_entry(DATABASE_PATH, entry_id)
    return redirect(url_for('history'))


@app.route('/history')
@login_required
def history():
    user_id = session['user_id']
    entries = get_entries_for_user(DATABASE_PATH, user_id)
    return render_template('history.html', entries=entries)


@app.route('/weekly')
@login_required
def weekly():
    user_id = session['user_id']
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=6)
    entries = get_entries_in_range(DATABASE_PATH, user_id, week_start.isoformat(), today.isoformat())
    reflection = generate_weekly_reflection(entries, user_id, DATABASE_PATH)
    tag_corr = tag_correlation(DATABASE_PATH, user_id, week_start.isoformat(), today.isoformat())
    return render_template('weekly.html', reflection=reflection, tag_corr=tag_corr)


@app.template_filter('mood_color')
def mood_color(mood_val):
    """Return a color for a mood value 0-10 (blue palette, minimalist)."""
    try:
        m = int(mood_val)
    except Exception:
        m = 5
    # soft pastel blue palette: white to soft blue
    palette = [
        '#ffffff', # 0 (white)
        '#f0f6ff', # 1
        '#e0ecff', # 2
        '#d0e3ff', # 3
        '#c0daff', # 4
        '#b0d0ff', # 5 (soft blue)
        '#a0c7ff', # 6
        '#90bfff', # 7
        '#80b6ff', # 8
        '#70aaff', # 9
        '#8eb4e0', #10 (medium blue - from design)
    ]
    idx = max(0, min(10, m))
    return palette[idx]


@app.template_filter('energy_color')
def energy_color(energy_val):
    """Return a color for an energy value 0-10 (sage green palette, minimalist)."""
    try:
        e = int(energy_val)
    except Exception:
        e = 5
    # soft pastel sage palette: white to sage green
    palette = [
        '#ffffff', # 0 (white)
        '#f5faf5', # 1
        '#eff6ed', # 2
        '#e9f1e4', # 3
        '#e3eddc', # 4
        '#dde8d4', # 5 (soft sage)
        '#d7e3cc', # 6
        '#d1dfc4', # 7
        '#cbdabc', # 8
        '#c5d5b4', # 9
        '#c8d695', #10 (medium sage - from design)
    ]
    idx = max(0, min(10, e))
    return palette[idx]


@app.template_filter('anxiety_color')
def anxiety_color(anxiety_val):
    """Return a color for an anxiety value 0-10 (coral palette, minimalist)."""
    try:
        a = int(anxiety_val)
    except Exception:
        a = 5
    # soft pastel coral palette: white to coral
    palette = [
        '#ffffff', # 0 (white)
        '#fff5f5', # 1
        '#ffeceb', # 2
        '#ffe3e1', # 3
        '#ffdad7', # 4
        '#ffd1ce', # 5 (soft coral)
        '#ffc8c5', # 6
        '#ffbfbb', # 7
        '#ffb6b2', # 8
        '#ffada9', # 9
        '#e8a8a8', #10 (medium coral - from design)
    ]
    idx = max(0, min(10, a))
    return palette[idx]


@app.route('/diary')
@login_required
def diary():
    user_id = session['user_id']
    q = request.args.get('q', '').strip()
    try:
        page = int(request.args.get('page', '1'))
    except ValueError:
        page = 1
    per_page = 50
    offset = (page - 1) * per_page
    entries = search_entries_for_user(DATABASE_PATH, user_id, q if q else None, per_page, offset)
    total = count_entries_for_user(DATABASE_PATH, user_id, q if q else None)
    total_pages = max(1, (total + per_page - 1) // per_page)
    return render_template('diary.html', entries=entries, q=q, page=page, total_pages=total_pages)


if __name__ == '__main__':
    app.run(debug=True)
