# Research Topics & Learnings
## CS50 Final Project - Reflect

This document lists all the topics researched and new skills acquired during the development of Reflect.

---

## 🧠 Formal Topics Researched

### 1. Flask 3.1.3 Framework & Deprecations
**Research Focus**: How to migrate from deprecated decorators

**Learning**:
- `@app.before_first_request` was removed in Flask 3.1
- Solution: Move initialization logic to import-time
- Impact: Database initialization now happens at app startup

**References**:
- Flask 3.1 release notes
- Stack Overflow migration guides
- Flask official documentation

---

### 2. SQLite Concurrency & Transactions
**Research Focus**: Database locking issues during bulk operations

**Learning**:
- SQLite supports limited concurrent writes
- Batch operations in single transaction reduce locks
- ACID properties (Atomicity, Consistency, Isolation, Durability)
- `conn.executescript()` vs `conn.execute()` differences

**Solution Applied**:
- Refactored `set_entry_tags()` to batch operations
- All tag insertions happen in single transaction
- Prevents database lock during seed data generation

---

### 3. Relational Database Design & Normalization
**Research Focus**: 3NF schema design with many-to-many relationships

**Learning**:
- Three Normal Forms (1NF, 2NF, 3NF)
- Junction tables for many-to-many relationships
- Foreign key constraints
- Data integrity and consistency

**Applied Design**:
```
users (1) -----> (N) entries (N) <---> (N) tags
                                  via entry_tags
```

---

### 4. SQL Injection Prevention & Security
**Research Focus**: Parameterized queries and security best practices

**Learning**:
- Never concatenate user input into SQL strings
- Always use parameterized queries with `?` placeholders
- Input validation and sanitization
- Least privilege principle for database access

**Implementation**:
- All 15+ database queries use parameterized SQL
- No string interpolation in SQL statements
- Type hints for parameter validation

---

### 5. Password Hashing & Cryptography
**Research Focus**: Secure password storage

**Learning**:
- Never store plain-text passwords
- Use cryptographic hashing (not encryption)
- Salt prevents rainbow table attacks
- Werkzeug uses PBKDF2 or similar algorithms

**Implementation**:
```python
password_hash = generate_password_hash(password)
check_password_hash(password_hash, input_password)
```

---

### 6. Zen Design Philosophy & Minimalism
**Research Focus**: Lojong app design principles

**Learning**:
- Minimalism emphasizes clarity and focus
- Whitespace is an active design element
- Calm aesthetics reduce cognitive load
- Simplicity improves usability

**Design Principles Applied**:
- Generous padding and margins
- Subtle shadows and borders
- Clean typography with letter-spacing
- Limited color palette (3 primary + pastels)

---

### 7. Color Theory & Accessibility
**Research Focus**: Pastel colors for accessibility

**Learning**:
- Color contrast ratios (WCAG standards)
- Pastels are less jarring than bright colors
- Color-blind friendly palettes
- Multiple visual cues (not just color)

**Color System**:
- Blue palette: Mood (calm, introspective)
- Green palette: Energy (growth, vitality)
- Coral palette: Anxiety (compassion, care)
- White for 0 values (neutral baseline)

---

### 8. Responsive Web Design
**Research Focus**: Mobile-first CSS and media queries

**Learning**:
- Mobile-first approach (start with mobile, enhance for desktop)
- CSS media queries for breakpoints
- Flexbox and CSS Grid for layouts
- Viewport meta tags for mobile rendering

**Breakpoints Used**:
- 640px: Mobile phones
- 980px: Tablets
- 1000px+: Desktop (default)

---

### 9. Chart.js Integration
**Research Focus**: Client-side data visualization

**Learning**:
- Chart.js provides diverse chart types
- Real-time chart updates with Canvas API
- Responsive chart sizing
- Data structure for charts (labels, datasets, options)

**Charts Implemented**:
- Line chart: 7-day mood trend
- Area chart: Energy + anxiety composite

---

### 10. Pagination Algorithms
**Research Focus**: Large dataset handling

**Learning**:
- Offset/limit pattern for pagination
- Total count calculation
- Previous/next navigation
- Page numbering

**Implementation**:
- 50 entries per page
- Efficient database queries
- Search-aware pagination

---

### 11. Full-Text Search
**Research Focus**: Keyword searching across multiple fields

**Learning**:
- SQL LIKE operator with wildcards
- Case-insensitive searching
- Searching across multiple columns
- Performance considerations

**Implementation**:
```sql
WHERE (event_description LIKE ? OR tags LIKE ?)
```

---

### 12. Statistical Analysis
**Research Focus**: Data analysis and correlation

**Learning**:
- Mean/average calculations
- Weighted scoring formulas
- Correlation analysis
- Trend detection

**Algorithms Implemented**:
- Weekly averages: `sum(values) / count`
- Emotional score: `mood×0.6 + energy×0.3 - anxiety×0.1`
- Tag correlation: tags sorted by avg mood

---

### 13. Flask Sessions & Authentication
**Research Focus**: Session management and user authentication

**Learning**:
- Session cookies store user state
- Session data persists across requests
- User isolation via user_id
- Login required pattern

**Implementation**:
- Custom `@login_required` decorator
- User ID stored in session
- All queries filtered by user_id

---

### 14. Jinja2 Template Engine
**Research Focus**: Server-side template rendering

**Learning**:
- Template inheritance and blocks
- Loops and conditionals in templates
- Custom template filters
- Escaping and security

**Filters Created**:
- `mood_color`: Maps 0-10 to blue palette
- `energy_color`: Maps 0-10 to green palette
- `anxiety_color`: Maps 0-10 to coral palette

---

### 15. CSS Custom Properties
**Research Focus**: Modern CSS practices

**Learning**:
- CSS variables (custom properties)
- Variable scoping
- Fallback values
- Dynamic styling

**Variables Used**:
```css
--bg: #faf9f7
--primary: #8eb4e0
--radius: 8px
--shadow-1: 0 2px 8px ...
```

---

## 🎯 Problem-Solving Case Studies

### Case Study 1: Flask Deprecation

**Problem**: 
- `@app.before_first_request` removed in Flask 3.1
- Tests failed on import

**Research**:
- Checked Flask 3.1 release notes
- Searched for migration patterns
- Read Flask documentation

**Solution**:
- Moved `init_db()` to import-time
- Database initializes when app.py is imported
- No decorator needed

**Outcome**: ✅ App imports successfully

---

### Case Study 2: Database Locking

**Problem**:
- Seed script fails with "database is locked"
- Flask holds connection while running

**Research**:
- Studied SQLite transaction management
- Learned about connection pooling
- Researched batch operations

**Solution**:
- Refactored `set_entry_tags()` to batch in single transaction
- All tag insertions happen atomically
- Reduced lock contention

**Outcome**: ✅ Seed script completes successfully

---

### Case Study 3: UI Design

**Problem**:
- Generic Bootstrap-style UI looks uninspired
- Doesn't match CS50 quality expectations

**Research**:
- Analyzed Lojong app design
- Studied zen design principles
- Researched pastel color theory
- Learned responsive design patterns

**Solution**:
- Implemented custom CSS from scratch
- Created zen aesthetic with whitespace
- Built pastel color system
- Made fully responsive layout

**Outcome**: ✅ Professional, calm UI that stands out

---

## 📚 Resources Used

### Official Documentation
- Flask: https://flask.palletsprojects.com/
- SQLite: https://www.sqlite.org/docs.html
- Python: https://docs.python.org/
- Werkzeug: https://werkzeug.palletsprojects.com/
- Chart.js: https://www.chartjs.org/

### Design Inspiration
- Lojong: https://lojongapp.com/
- WCAG Accessibility: https://www.w3.org/WAI/
- Zen Design: Various medium articles

### Learning Resources
- CS50: https://cs50.harvard.edu/
- Stack Overflow: Community Q&A
- MDN Web Docs: https://developer.mozilla.org/
- W3Schools: HTML/CSS reference

---

## 🏆 Key Takeaways

### What I Learned Most
1. **Architecture matters**: Proper layering makes everything easier
2. **Security is critical**: Parameterized queries aren't optional
3. **Design is important**: Good UX significantly improves user experience
4. **Testing is essential**: Finding bugs early saves time later
5. **Documentation helps**: Clear code comments save future self

### Skills I'm Most Proud Of
1. ✨ Designing and implementing a professional UI
2. 🔐 Implementing security best practices from day one
3. 📊 Creating meaningful analytics algorithms
4. 🏗️ Clean architecture that's easy to maintain
5. 🐛 Systematic debugging of tricky issues

### Areas for Future Growth
- Caching strategies (Redis, memcached)
- Scaling to PostgreSQL
- API design (REST/GraphQL)
- Automated testing (pytest, Selenium)
- Deployment (Docker, cloud platforms)
- Machine learning for trend prediction

---

## 📖 Conclusion

The research and learning process for this project far exceeded simple Googling. It involved:

- ✅ Deep dives into framework documentation
- ✅ Understanding design philosophy
- ✅ Learning security best practices
- ✅ Solving real problems with creative solutions
- ✅ Continuous learning and iteration

This project demonstrates that **CS50 taught me how to learn**, not just how to code.

