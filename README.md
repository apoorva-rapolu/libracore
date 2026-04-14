# LibraCore — Flask + SQLite
## Architecture

```
Browser (HTML/JS)
      ↕  HTTP requests (fetch API)
Flask Server  [app.py]   ← Python backend
      ↕  sqlite3 module
libracore.db              ← SQLite database file (persists on disk)
```

## Setup & Run

### 1. Install Python (if not installed)
Download from https://python.org — version 3.8 or above.

### 2. Install Flask
Open a terminal in this folder and run:
```
pip install flask
```
Or use the requirements file:
```
pip install -r requirements.txt
```

### 3. Run the server
```
python app.py
```

## Login Credentials

| Role       | Username | Password |
|------------|----------|----------|
| Librarian  | admin1   | admin123 |
| Member     | (select) | pass123  |

---

## Project Structure

```
libracore/
├── app.py              ← Flask backend (all routes + DB logic)
├── libracore.db        ← SQLite database (auto-created on first run)
├── requirements.txt    ← Python dependencies
├── templates/
│   ├── index.html      ← Login page
│   └── app.html        ← Main app (SPA, fetches data from API)
└── README.md
```

## API Endpoints

| Method | Route                       | Description              |
|--------|-----------------------------|--------------------------|
| POST   | /login                      | Authenticate user        |
| GET    | /logout                     | Clear session            |
| GET    | /api/stats                  | Dashboard stats          |
| GET    | /api/books                  | All books                |
| POST   | /api/books                  | Add a book               |
| GET    | /api/copies                 | Book copies + rack info  |
| GET    | /api/authors                | Authors                  |
| GET    | /api/members                | All members              |
| POST   | /api/members                | Add a member             |
| GET    | /api/issues                 | All issue transactions   |
| POST   | /api/issues                 | Issue a book             |
| GET    | /api/returns                | All return transactions  |
| POST   | /api/returns                | Record a return          |
| GET    | /api/overdue                | Currently overdue books  |
| GET    | /api/fines                  | Fine records             |
| GET    | /api/reservations           | Reservations             |
| POST   | /api/sql                    | Run raw SQL (librarian)  |

## Notes
- The database file `libracore.db` is created automatically on first run.
- Data **persists** between runs — it is a real file on disk.
- The SQL Runner tab lets you run any SQL query live against the actual database.
- Fine calculation: Rs. 5 per day overdue (auto-computed on return).
