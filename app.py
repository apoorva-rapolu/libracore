"""
LibraCore — Flask + SQLite Backend
Lab No. 6 · Mini Project Phase I
Run:  python app.py
Then: open http://localhost:5000
"""

import sqlite3, os
from datetime import date, timedelta
from flask import Flask, g, jsonify, request, render_template, session, redirect, url_for

# ✅ DEFINE DB PATH FIRST
DB_PATH = os.path.join(os.path.dirname(__file__), "libracore.db")

def create_admin():
    conn = sqlite3.connect(DB_PATH)   # ✅ FIXED HERE
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT,
        password TEXT
    )
    ''')

    cursor.execute("SELECT * FROM users WHERE username = 'admin1'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?)", ("admin1", "admin123"))

    conn.commit()
    conn.close()

# ✅ CALL FUNCTION
create_admin()

app = Flask(__name__)
app.secret_key = "libracore-secret-2024"
DB_PATH = os.path.join(os.path.dirname(__file__), "libracore.db")

# ─────────────────────────────────────────
#  DATABASE CONNECTION HELPERS
# ─────────────────────────────────────────
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row          # rows behave like dicts
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db:
        db.close()

def query(sql, params=()):
    """Run a SELECT, return list of dicts."""
    cur = get_db().execute(sql, params)
    return [dict(r) for r in cur.fetchall()]

def run(sql, params=()):
    """Run INSERT / UPDATE / DELETE, commit, return lastrowid."""
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur.lastrowid

# ─────────────────────────────────────────
#  DB INIT — create tables + seed data
# ─────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS Publishers (
    publisher_id INTEGER PRIMARY KEY,
    name TEXT, address TEXT, contact TEXT
);
CREATE TABLE IF NOT EXISTS Category (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT
);
CREATE TABLE IF NOT EXISTS Authors (
    author_id INTEGER PRIMARY KEY,
    name TEXT, country TEXT
);
CREATE TABLE IF NOT EXISTS Books (
    book_id INTEGER PRIMARY KEY,
    title TEXT, isbn TEXT,
    publisher_id INTEGER, category_id INTEGER,
    language TEXT, edition INTEGER, year_published INTEGER,
    FOREIGN KEY (publisher_id) REFERENCES Publishers(publisher_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);
CREATE TABLE IF NOT EXISTS Book_Authors (
    book_id INTEGER, author_id INTEGER,
    PRIMARY KEY (book_id, author_id)
);
CREATE TABLE IF NOT EXISTS Rack (
    rack_id INTEGER PRIMARY KEY,
    rack_number TEXT, section TEXT
);
CREATE TABLE IF NOT EXISTS Book_Copies (
    copy_id INTEGER PRIMARY KEY,
    book_id INTEGER, status TEXT, rack_id INTEGER,
    FOREIGN KEY (book_id) REFERENCES Books(book_id),
    FOREIGN KEY (rack_id) REFERENCES Rack(rack_id)
);
CREATE TABLE IF NOT EXISTS Members (
    member_id INTEGER PRIMARY KEY,
    name TEXT, email TEXT, phone TEXT,
    membership_type TEXT, membership_date TEXT,
    status TEXT, password TEXT
);
CREATE TABLE IF NOT EXISTS Staff (
    staff_id INTEGER PRIMARY KEY,
    name TEXT, role TEXT, email TEXT, phone TEXT
);
CREATE TABLE IF NOT EXISTS User_Account (
    user_id INTEGER PRIMARY KEY,
    member_id INTEGER, staff_id INTEGER,
    username TEXT, password TEXT, role TEXT
);
CREATE TABLE IF NOT EXISTS Issue_Transaction (
    issue_id INTEGER PRIMARY KEY,
    copy_id INTEGER, member_id INTEGER, staff_id INTEGER,
    issue_date TEXT, due_date TEXT
);
CREATE TABLE IF NOT EXISTS Return_Transaction (
    return_id INTEGER PRIMARY KEY,
    issue_id INTEGER, return_date TEXT
);
CREATE TABLE IF NOT EXISTS Fine (
    fine_id INTEGER PRIMARY KEY,
    return_id INTEGER, amount INTEGER, paid_status TEXT
);
CREATE TABLE IF NOT EXISTS Payment (
    payment_id INTEGER PRIMARY KEY,
    fine_id INTEGER, payment_date TEXT,
    amount INTEGER, payment_method TEXT
);
CREATE TABLE IF NOT EXISTS Reservation (
    reservation_id INTEGER PRIMARY KEY,
    member_id INTEGER, book_id INTEGER,
    reservation_date TEXT, status TEXT
);
"""

def seed_db():
    today = date.today().isoformat()
    def ago(n): return (date.today() - timedelta(days=n)).isoformat()
    def ahead(n): return (date.today() + timedelta(days=n)).isoformat()

    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)

    # Only seed if empty
    if db.execute("SELECT COUNT(*) FROM Books").fetchone()[0] > 0:
        db.close()
        return

    seed = f"""
    INSERT INTO Publishers VALUES (1,'Penguin Books','USA','1234567890');
    INSERT INTO Publishers VALUES (2,'HarperCollins','UK','9876543210');
    INSERT INTO Publishers VALUES (3,'Oxford Press','UK','1112223333');
    INSERT INTO Publishers VALUES (4,'McGraw Hill','USA','4445556666');
    INSERT INTO Publishers VALUES (5,'Pearson','India','7778889999');

    INSERT INTO Category VALUES (1,'Fiction');
    INSERT INTO Category VALUES (2,'Science');
    INSERT INTO Category VALUES (3,'Technology');
    INSERT INTO Category VALUES (4,'History');
    INSERT INTO Category VALUES (5,'Philosophy');
    INSERT INTO Category VALUES (6,'Mathematics');

    INSERT INTO Authors VALUES (1,'J.K. Rowling','UK');
    INSERT INTO Authors VALUES (2,'George Orwell','UK');
    INSERT INTO Authors VALUES (3,'Dan Brown','USA');
    INSERT INTO Authors VALUES (4,'Stephen Hawking','UK');
    INSERT INTO Authors VALUES (5,'Andrew Ng','USA');
    INSERT INTO Authors VALUES (6,'Yuval Noah Harari','Israel');
    INSERT INTO Authors VALUES (7,'Cormen','USA');
    INSERT INTO Authors VALUES (8,'Russell','USA');
    INSERT INTO Authors VALUES (9,'Norvig','USA');

    INSERT INTO Books VALUES (1,'Harry Potter','1111',1,1,'English',1,1997);
    INSERT INTO Books VALUES (2,'1984','2222',2,1,'English',1,1949);
    INSERT INTO Books VALUES (3,'Da Vinci Code','3333',2,1,'English',1,2003);
    INSERT INTO Books VALUES (4,'Brief History of Time','4444',3,2,'English',1,1988);
    INSERT INTO Books VALUES (5,'Machine Learning Basics','5555',4,3,'English',2,2020);
    INSERT INTO Books VALUES (6,'Sapiens','6666',5,4,'English',1,2011);
    INSERT INTO Books VALUES (7,'Introduction to Algorithms','7777',4,6,'English',3,2009);
    INSERT INTO Books VALUES (8,'Artificial Intelligence','8888',4,3,'English',2,2015);
    INSERT INTO Books VALUES (9,'Philosophy 101','9999',3,5,'English',1,2018);
    INSERT INTO Books VALUES (10,'Calculus Made Easy','1010',5,6,'English',1,2012);

    INSERT INTO Book_Authors VALUES (1,1);
    INSERT INTO Book_Authors VALUES (2,2);
    INSERT INTO Book_Authors VALUES (3,3);
    INSERT INTO Book_Authors VALUES (4,4);
    INSERT INTO Book_Authors VALUES (5,5);
    INSERT INTO Book_Authors VALUES (6,6);
    INSERT INTO Book_Authors VALUES (7,7);
    INSERT INTO Book_Authors VALUES (8,8);
    INSERT INTO Book_Authors VALUES (8,9);
    INSERT INTO Book_Authors VALUES (9,6);
    INSERT INTO Book_Authors VALUES (10,7);

    INSERT INTO Rack VALUES (1,'R1','A');
    INSERT INTO Rack VALUES (2,'R2','A');
    INSERT INTO Rack VALUES (3,'R3','B');
    INSERT INTO Rack VALUES (4,'R4','B');
    INSERT INTO Rack VALUES (5,'R5','C');
    INSERT INTO Rack VALUES (6,'R6','C');

    INSERT INTO Book_Copies VALUES (1,1,'available',1);
    INSERT INTO Book_Copies VALUES (2,1,'issued',1);
    INSERT INTO Book_Copies VALUES (3,1,'available',2);
    INSERT INTO Book_Copies VALUES (4,2,'available',2);
    INSERT INTO Book_Copies VALUES (5,2,'issued',2);
    INSERT INTO Book_Copies VALUES (6,3,'available',3);
    INSERT INTO Book_Copies VALUES (7,3,'damaged',3);
    INSERT INTO Book_Copies VALUES (8,4,'available',3);
    INSERT INTO Book_Copies VALUES (9,5,'available',4);
    INSERT INTO Book_Copies VALUES (10,5,'issued',4);
    INSERT INTO Book_Copies VALUES (11,6,'available',5);
    INSERT INTO Book_Copies VALUES (12,7,'available',5);
    INSERT INTO Book_Copies VALUES (13,8,'issued',6);
    INSERT INTO Book_Copies VALUES (14,9,'available',6);
    INSERT INTO Book_Copies VALUES (15,10,'available',6);

    INSERT INTO Members VALUES (1,'Diya','diya@email.com','9999999999','student','{today}','active','pass123');
    INSERT INTO Members VALUES (2,'Niharika','niha@email.com','8888888888','student','{today}','active','pass123');
    INSERT INTO Members VALUES (3,'Apoorva','apoorva@email.com','7777777777','student','{today}','active','pass123');
    INSERT INTO Members VALUES (4,'Rahul','rahul@email.com','6666666666','faculty','{today}','active','pass123');
    INSERT INTO Members VALUES (5,'Sneha','sneha@email.com','5555555555','student','{today}','inactive','pass123');
    INSERT INTO Members VALUES (6,'Arjun','arjun@email.com','4444444444','student','{today}','active','pass123');
    INSERT INTO Members VALUES (7,'Meera','meera@email.com','3333333333','faculty','{today}','active','pass123');

    INSERT INTO Staff VALUES (1,'Admin1','librarian','admin1@lib.com','7777777777');
    INSERT INTO Staff VALUES (2,'Admin2','assistant','admin2@lib.com','6666666666');
    INSERT INTO Staff VALUES (3,'Admin3','librarian','admin3@lib.com','5555555555');

    INSERT INTO User_Account VALUES (1,1,NULL,'diya_user','pass123','member');
    INSERT INTO User_Account VALUES (2,2,NULL,'niha_user','pass123','member');
    INSERT INTO User_Account VALUES (3,NULL,1,'admin1','admin123','admin');
    INSERT INTO User_Account VALUES (4,NULL,2,'staff2','staff123','staff');

    INSERT INTO Issue_Transaction VALUES (1,2,1,1,'{ago(10)}','{ago(3)}');
    INSERT INTO Issue_Transaction VALUES (2,5,2,2,'{ago(5)}','{ahead(2)}');
    INSERT INTO Issue_Transaction VALUES (3,10,3,1,'{ago(8)}','{ago(1)}');
    INSERT INTO Issue_Transaction VALUES (4,4,4,3,'{ago(2)}','{ahead(5)}');
    INSERT INTO Issue_Transaction VALUES (5,13,6,2,'{ago(6)}','{ago(2)}');

    INSERT INTO Return_Transaction VALUES (1,1,'{ago(2)}');
    INSERT INTO Return_Transaction VALUES (2,3,'{today}');
    INSERT INTO Return_Transaction VALUES (3,5,'{today}');

    INSERT INTO Fine VALUES (1,1,50,'unpaid');
    INSERT INTO Fine VALUES (2,2,0,'paid');
    INSERT INTO Fine VALUES (3,3,20,'unpaid');

    INSERT INTO Payment VALUES (1,2,'{today}',0,'Cash');
    INSERT INTO Payment VALUES (2,1,'{today}',50,'UPI');
    INSERT INTO Payment VALUES (3,3,'{today}',20,'Card');

    INSERT INTO Reservation VALUES (1,1,2,'{today}','active');
    INSERT INTO Reservation VALUES (2,2,1,'{today}','fulfilled');
    INSERT INTO Reservation VALUES (3,3,5,'{today}','active');
    INSERT INTO Reservation VALUES (4,4,3,'{today}','cancelled');
    INSERT INTO Reservation VALUES (5,6,8,'{today}','active');
    """
    db.executescript(seed)
    db.commit()
    db.close()

# ─────────────────────────────────────────
#  AUTH ROUTES
# ─────────────────────────────────────────
@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    role_type = data.get("role_type")  # 'librarian' or 'member'

    if role_type == "librarian":
        username = data.get("username", "").strip()
        password = data.get("password", "")
        rows = query("""
            SELECT ua.*, s.name as staff_name, s.role as staff_role
            FROM User_Account ua
            LEFT JOIN Staff s ON ua.staff_id = s.staff_id
            WHERE ua.username=? AND ua.password=? AND ua.role IN ('admin','staff')
        """, (username, password))
        if rows:
            u = rows[0]
            session["user"] = {
                "id": u["user_id"], "name": u["staff_name"] or username,
                "role": "librarian", "staff_role": u["staff_role"]
            }
            return jsonify({"ok": True, "redirect": "/dashboard"})
        return jsonify({"ok": False, "error": "Invalid credentials."})

    elif role_type == "member":
        member_id = data.get("member_id")
        password  = data.get("password", "")
        rows = query(
            "SELECT * FROM Members WHERE member_id=? AND password=?",
            (member_id, password)
        )
        if rows:
            m = rows[0]
            session["user"] = {
                "id": m["member_id"], "name": m["name"],
                "role": "member", "membership_type": m["membership_type"],
                "member_id": m["member_id"]
            }
            return jsonify({"ok": True, "redirect": "/dashboard"})
        return jsonify({"ok": False, "error": "Invalid password."})

    return jsonify({"ok": False, "error": "Unknown role."})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper

def librarian_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session or session["user"]["role"] != "librarian":
            return jsonify({"error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return wrapper

# ─────────────────────────────────────────
#  MAIN APP PAGE (SPA shell)
# ─────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("app.html", user=session["user"])

# ─────────────────────────────────────────
#  API — DASHBOARD STATS
# ─────────────────────────────────────────
@app.route("/api/stats")
@login_required
def api_stats():
    today = date.today().isoformat()
    if session["user"]["role"] == "librarian":
        return jsonify({
            "total_books":   query("SELECT COUNT(*) as n FROM Books")[0]["n"],
            "active_members":query("SELECT COUNT(*) as n FROM Members WHERE status='active'")[0]["n"],
            "issued_copies": query("SELECT COUNT(*) as n FROM Book_Copies WHERE status='issued'")[0]["n"],
            "unpaid_fines":  query("SELECT COALESCE(SUM(amount),0) as n FROM Fine WHERE paid_status='unpaid'")[0]["n"],
            "recent_issues": query("""
                SELECT m.name as member, b.title, i.issue_date, i.due_date
                FROM Issue_Transaction i
                JOIN Members m ON i.member_id=m.member_id
                JOIN Book_Copies bc ON i.copy_id=bc.copy_id
                JOIN Books b ON bc.book_id=b.book_id
                ORDER BY i.issue_date DESC LIMIT 5"""),
            "category_counts": query("""
                SELECT c.category_name, COUNT(b.book_id) as cnt
                FROM Books b JOIN Category c ON b.category_id=c.category_id
                GROUP BY c.category_name ORDER BY cnt DESC"""),
        })
    else:
        mid = session["user"]["member_id"]
        fines = query("""
            SELECT COALESCE(SUM(f.amount),0) as total,
                   SUM(CASE WHEN f.paid_status='unpaid' THEN f.amount ELSE 0 END) as unpaid
            FROM Fine f
            JOIN Return_Transaction r ON f.return_id=r.return_id
            JOIN Issue_Transaction i ON r.issue_id=i.issue_id
            WHERE i.member_id=?""", (mid,))
        issues = query("""
            SELECT b.title, i.issue_date, i.due_date,
                   CASE WHEN rt.return_id IS NOT NULL THEN 'returned' ELSE 'issued' END as status
            FROM Issue_Transaction i
            JOIN Book_Copies bc ON i.copy_id=bc.copy_id
            JOIN Books b ON bc.book_id=b.book_id
            LEFT JOIN Return_Transaction rt ON rt.issue_id=i.issue_id
            WHERE i.member_id=? ORDER BY i.issue_date DESC""", (mid,))
        return jsonify({
            "my_issues": issues,
            "total_fines": fines[0]["total"] if fines else 0,
            "unpaid_fines": fines[0]["unpaid"] if fines else 0,
            "active_issues": sum(1 for r in issues if r["status"] == "issued"),
        })

# ─────────────────────────────────────────
#  API — BOOKS
# ─────────────────────────────────────────
@app.route("/api/books")
@login_required
def api_books():
    rows = query("""
        SELECT b.book_id, b.title, b.isbn, b.year_published, b.edition,
               GROUP_CONCAT(DISTINCT a.name) as authors,
               c.category_name, p.name as publisher,
               SUM(CASE WHEN bc.status='available' THEN 1 ELSE 0 END) as avail,
               COUNT(bc.copy_id) as total
        FROM Books b
        LEFT JOIN Book_Authors ba ON b.book_id=ba.book_id
        LEFT JOIN Authors a ON ba.author_id=a.author_id
        JOIN Category c ON b.category_id=c.category_id
        JOIN Publishers p ON b.publisher_id=p.publisher_id
        LEFT JOIN Book_Copies bc ON b.book_id=bc.book_id
        GROUP BY b.book_id ORDER BY b.title""")
    return jsonify(rows)

@app.route("/api/books", methods=["POST"])
@librarian_required
def api_add_book():
    d = request.json
    new_id = query("SELECT COALESCE(MAX(book_id),0)+1 as id FROM Books")[0]["id"]
    run("INSERT INTO Books VALUES (?,?,?,?,?,?,?,?)",
        (new_id, d["title"], d.get("isbn",""), d["publisher_id"],
         d["category_id"], "English", d.get("edition",1), d.get("year_published", date.today().year)))
    return jsonify({"ok": True, "book_id": new_id})

@app.route("/api/categories")
@login_required
def api_categories():
    return jsonify(query("SELECT * FROM Category ORDER BY category_name"))

@app.route("/api/publishers")
@login_required
def api_publishers():
    return jsonify(query("SELECT * FROM Publishers ORDER BY name"))

# ─────────────────────────────────────────
#  API — COPIES
# ─────────────────────────────────────────
@app.route("/api/copies")
@login_required
def api_copies():
    rows = query("""
        SELECT bc.copy_id, b.title, bc.status, rk.rack_number, rk.section
        FROM Book_Copies bc
        JOIN Books b ON bc.book_id=b.book_id
        JOIN Rack rk ON bc.rack_id=rk.rack_id
        ORDER BY bc.copy_id""")
    return jsonify(rows)

# ─────────────────────────────────────────
#  API — AUTHORS
# ─────────────────────────────────────────
@app.route("/api/authors")
@login_required
def api_authors():
    rows = query("""
        SELECT a.author_id, a.name, a.country,
               COUNT(ba.book_id) as book_count,
               GROUP_CONCAT(b.title, ', ') as books
        FROM Authors a
        LEFT JOIN Book_Authors ba ON a.author_id=ba.author_id
        LEFT JOIN Books b ON ba.book_id=b.book_id
        GROUP BY a.author_id ORDER BY a.name""")
    return jsonify(rows)

# ─────────────────────────────────────────
#  API — MEMBERS
# ─────────────────────────────────────────
@app.route("/api/members")
@librarian_required
def api_members():
    rows = query("""
        SELECT m.*, COUNT(i.issue_id) as total_issues
        FROM Members m
        LEFT JOIN Issue_Transaction i ON m.member_id=i.member_id
        GROUP BY m.member_id ORDER BY m.name""")
    return jsonify(rows)

@app.route("/api/members", methods=["POST"])
@librarian_required
def api_add_member():
    d = request.json
    new_id = query("SELECT COALESCE(MAX(member_id),0)+1 as id FROM Members")[0]["id"]
    run("INSERT INTO Members VALUES (?,?,?,?,?,?,?,?)",
        (new_id, d["name"], d["email"], d.get("phone",""),
         d.get("membership_type","student"), date.today().isoformat(),
         "active", d.get("password","pass123")))
    return jsonify({"ok": True, "member_id": new_id})

@app.route("/api/members/active")
@login_required
def api_members_active():
    return jsonify(query("SELECT member_id, name, membership_type FROM Members WHERE status='active' ORDER BY name"))

# ─────────────────────────────────────────
#  API — ISSUES
# ─────────────────────────────────────────
@app.route("/api/issues")
@librarian_required
def api_issues():
    today = date.today().isoformat()
    rows = query(f"""
        SELECT i.issue_id, m.name as member, b.title,
               bc.copy_id, i.issue_date, i.due_date,
               CASE WHEN rt.return_id IS NOT NULL THEN 'returned' ELSE 'active' END as state,
               CASE WHEN i.due_date < '{today}' AND rt.return_id IS NULL THEN 1 ELSE 0 END as is_overdue
        FROM Issue_Transaction i
        JOIN Members m ON i.member_id=m.member_id
        JOIN Book_Copies bc ON i.copy_id=bc.copy_id
        JOIN Books b ON bc.book_id=b.book_id
        LEFT JOIN Return_Transaction rt ON rt.issue_id=i.issue_id
        ORDER BY i.issue_date DESC""")
    return jsonify(rows)

@app.route("/api/issues", methods=["POST"])
@librarian_required
def api_issue_book():
    d = request.json
    mid  = d["member_id"]
    cid  = d["copy_id"]
    days = int(d.get("due_days", 14))
    today = date.today().isoformat()
    due   = (date.today() + timedelta(days=days)).isoformat()

    # Check member active
    m = query("SELECT status FROM Members WHERE member_id=?", (mid,))
    if not m or m[0]["status"] != "active":
        return jsonify({"ok": False, "error": "Member is inactive."}), 400

    # Check copy available
    c = query("SELECT status FROM Book_Copies WHERE copy_id=?", (cid,))
    if not c or c[0]["status"] != "available":
        return jsonify({"ok": False, "error": "Copy is not available."}), 400

    new_id = query("SELECT COALESCE(MAX(issue_id),0)+1 as id FROM Issue_Transaction")[0]["id"]
    run("INSERT INTO Issue_Transaction VALUES (?,?,?,?,?,?)",
        (new_id, cid, mid, 1, today, due))
    run("UPDATE Book_Copies SET status='issued' WHERE copy_id=?", (cid,))
    return jsonify({"ok": True, "issue_id": new_id})

@app.route("/api/issues/available-copies")
@librarian_required
def api_available_copies():
    rows = query("""
        SELECT bc.copy_id, b.title || ' (Copy #' || bc.copy_id || ')' as label
        FROM Book_Copies bc JOIN Books b ON bc.book_id=b.book_id
        WHERE bc.status='available' ORDER BY b.title""")
    return jsonify(rows)

# ─────────────────────────────────────────
#  API — RETURNS
# ─────────────────────────────────────────
@app.route("/api/returns")
@librarian_required
def api_returns():
    rows = query("""
        SELECT rt.return_id, m.name as member, b.title,
               rt.return_date, i.due_date, f.amount, f.paid_status
        FROM Return_Transaction rt
        JOIN Issue_Transaction i ON rt.issue_id=i.issue_id
        JOIN Members m ON i.member_id=m.member_id
        JOIN Book_Copies bc ON i.copy_id=bc.copy_id
        JOIN Books b ON bc.book_id=b.book_id
        LEFT JOIN Fine f ON f.return_id=rt.return_id
        ORDER BY rt.return_date DESC""")
    return jsonify(rows)

@app.route("/api/returns", methods=["POST"])
@librarian_required
def api_return_book():
    d   = request.json
    iid = int(d["issue_id"])
    today = date.today().isoformat()

    # Get issue info
    issue = query("SELECT * FROM Issue_Transaction WHERE issue_id=?", (iid,))
    if not issue:
        return jsonify({"ok": False, "error": "Issue not found."}), 404
    issue = issue[0]

    # Check not already returned
    existing = query("SELECT * FROM Return_Transaction WHERE issue_id=?", (iid,))
    if existing:
        return jsonify({"ok": False, "error": "Already returned."}), 400

    new_rid = query("SELECT COALESCE(MAX(return_id),0)+1 as id FROM Return_Transaction")[0]["id"]
    run("INSERT INTO Return_Transaction VALUES (?,?,?)", (new_rid, iid, today))

    # Auto fine: Rs 5/day
    from datetime import datetime
    due = datetime.fromisoformat(issue["due_date"]).date()
    ret = datetime.fromisoformat(today).date()
    days_late = max(0, (ret - due).days)
    fine_amt  = days_late * 5

    new_fid = query("SELECT COALESCE(MAX(fine_id),0)+1 as id FROM Fine")[0]["id"]
    run("INSERT INTO Fine VALUES (?,?,?,?)",
        (new_fid, new_rid, fine_amt, "paid" if fine_amt == 0 else "unpaid"))

    # Free the copy
    run("UPDATE Book_Copies SET status='available' WHERE copy_id=?", (issue["copy_id"],))

    return jsonify({"ok": True, "fine": fine_amt, "days_late": days_late})

@app.route("/api/returns/active-issues")
@librarian_required
def api_active_issues():
    rows = query("""
        SELECT i.issue_id,
               m.name || ' — ' || b.title || ' (Copy #' || bc.copy_id || ')' as label
        FROM Issue_Transaction i
        JOIN Members m ON i.member_id=m.member_id
        JOIN Book_Copies bc ON i.copy_id=bc.copy_id
        JOIN Books b ON bc.book_id=b.book_id
        LEFT JOIN Return_Transaction rt ON rt.issue_id=i.issue_id
        WHERE rt.return_id IS NULL ORDER BY i.issue_date""")
    return jsonify(rows)

# ─────────────────────────────────────────
#  API — OVERDUE
# ─────────────────────────────────────────
@app.route("/api/overdue")
@librarian_required
def api_overdue():
    today = date.today().isoformat()
    rows = query(f"""
        SELECT m.name as member, b.title, i.due_date,
               CAST(julianday('{today}') - julianday(i.due_date) AS INTEGER) as days_late
        FROM Issue_Transaction i
        JOIN Members m ON i.member_id=m.member_id
        JOIN Book_Copies bc ON i.copy_id=bc.copy_id
        JOIN Books b ON bc.book_id=b.book_id
        LEFT JOIN Return_Transaction rt ON rt.issue_id=i.issue_id
        WHERE i.due_date < '{today}' AND rt.return_id IS NULL
        ORDER BY days_late DESC""")
    return jsonify(rows)

# ─────────────────────────────────────────
#  API — RESERVATIONS
# ─────────────────────────────────────────
@app.route("/api/reservations")
@login_required
def api_reservations():
    mid = session["user"].get("member_id")
    if session["user"]["role"] == "librarian":
        rows = query("""
            SELECT r.reservation_id, m.name as member, b.title,
                   r.reservation_date, r.status
            FROM Reservation r
            JOIN Members m ON r.member_id=m.member_id
            JOIN Books b ON r.book_id=b.book_id
            ORDER BY r.reservation_date DESC""")
    else:
        rows = query("""
            SELECT b.title, r.reservation_date, r.status
            FROM Reservation r JOIN Books b ON r.book_id=b.book_id
            WHERE r.member_id=? ORDER BY r.reservation_date DESC""", (mid,))
    return jsonify(rows)

# ─────────────────────────────────────────
#  API — FINES
# ─────────────────────────────────────────
@app.route("/api/fines")
@login_required
def api_fines():
    mid = session["user"].get("member_id")
    if session["user"]["role"] == "librarian":
        rows = query("""
            SELECT f.fine_id, m.name as member, b.title,
                   rt.return_date, f.amount, f.paid_status,
                   p.payment_method, p.payment_date
            FROM Fine f
            JOIN Return_Transaction rt ON f.return_id=rt.return_id
            JOIN Issue_Transaction i ON rt.issue_id=i.issue_id
            JOIN Members m ON i.member_id=m.member_id
            JOIN Book_Copies bc ON i.copy_id=bc.copy_id
            JOIN Books b ON bc.book_id=b.book_id
            LEFT JOIN Payment p ON p.fine_id=f.fine_id
            ORDER BY f.fine_id""")
    else:
        rows = query("""
            SELECT b.title, f.amount, f.paid_status,
                   p.payment_method, p.payment_date
            FROM Fine f
            JOIN Return_Transaction rt ON f.return_id=rt.return_id
            JOIN Issue_Transaction i ON rt.issue_id=i.issue_id
            JOIN Book_Copies bc ON i.copy_id=bc.copy_id
            JOIN Books b ON bc.book_id=b.book_id
            LEFT JOIN Payment p ON p.fine_id=f.fine_id
            WHERE i.member_id=?""", (mid,))
    return jsonify(rows)

@app.route("/api/fines/summary")
@login_required
def api_fines_summary():
    return jsonify(query("""
        SELECT COALESCE(SUM(amount),0) as total,
               SUM(CASE WHEN paid_status='unpaid' THEN amount ELSE 0 END) as unpaid
        FROM Fine""")[0])

# ─────────────────────────────────────────
#  API — SQL RUNNER (librarian only)
# ─────────────────────────────────────────
@app.route("/api/sql", methods=["POST"])
@librarian_required
def api_sql():
    import time
    q = request.json.get("query", "").strip()
    if not q:
        return jsonify({"ok": False, "error": "Empty query."})
    try:
        db = get_db()
        t0 = time.time()
        # Split statements
        statements = [s.strip() for s in q.split(";") if s.strip()]
        rows, cols = [], []
        msg = None
        for stmt in statements:
            upper = stmt.upper().lstrip()
            if upper.startswith("SELECT") or upper.startswith("WITH"):
                cur = db.execute(stmt)
                cols = [d[0] for d in cur.description] if cur.description else []
                rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            else:
                cur = db.execute(stmt)
                db.commit()
                msg = f"Query executed. {cur.rowcount} row(s) affected."
        ms = round((time.time() - t0) * 1000, 1)
        return jsonify({"ok": True, "rows": rows, "cols": cols, "ms": ms, "msg": msg})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    seed_db()
    print("\n" + "="*50)
    print("  LibraCore is running!")
    print("  Open: http://localhost:5000")
    print("  Librarian: admin1 / admin123")
    print("  Member password: pass123")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)
