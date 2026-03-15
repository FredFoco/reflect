# Reflect — Structured Journaling and Emotional Self-Tracking

Reflect is a local Flask web application designed for structured journaling and self-awareness. It helps users track mood, energy, and anxiety and provides weekly analytics and reflections.

## Project idea

- Not a therapy tool — a self-awareness app to identify patterns.
- Users record daily entries with mood, energy, anxiety, a description, and tags.

## Architecture & design decisions

- Python + Flask for simplicity and CS50 compatibility.
- SQLite for a lightweight local relational database.
- Small service-layer separation:
  - `database.py` — all DB schema and parameterized queries
  - `helpers.py` — business logic and analytics (weekly averages, reflections, streaks)
  - `app.py` — Flask routes and glue
- Jinja templates in `/templates`, static CSS in `/static`.
- Chart.js (CDN) for front-end visualizations.

## Database schema

- `users` (id, username, password_hash)
- `entries` (id, user_id, date, mood, energy, anxiety, event_description)
- `tags` (id, name)
- `entry_tags` (entry_id, tag_id) — many-to-many relationship

All queries use parameterized SQL to avoid injection.

## Key features

- User registration, login, logout with password hashing.
- Create, edit, delete entries.
- Tagging (multiple tags per entry).
- Dashboard with weekly averages, streak count, and charts for mood/energy/anxiety.
- Weekly reflection generator comparing to previous week.
- Advanced: streak tracking and emotional composite score. Tag correlation shows which tags associate with lower mood.

## Running locally

1. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:

```bash
export FLASK_APP=app.py
flask run
```

Open http://127.0.0.1:5000 in your browser.

## Files of interest

- `app.py` — Flask app and routes
- `database.py` — DB schema and helpers
- `helpers.py` — analytics and reflection generator
- `templates/` — Jinja templates
- `static/styles.css` — minimal styling

## Notes & Next steps

- This project focuses on clear separation between DB, logic, and routes. For production use, add CSRF protection, stronger session management, and input validation.
