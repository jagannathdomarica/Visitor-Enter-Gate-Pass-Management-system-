import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__, template_folder=".", static_folder=".", static_url_path="/static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-visitor-entry-system")
DB_PATH = os.path.join(os.path.dirname(__file__), "visitors.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'staff'
        );
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            company TEXT,
            purpose TEXT,
            vehicle_number TEXT,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            created_by INTEGER,
            FOREIGN KEY(created_by) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS gatepasses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id INTEGER NOT NULL,
            pass_number TEXT NOT NULL,
            valid_from TEXT NOT NULL,
            valid_to TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            FOREIGN KEY(visitor_id) REFERENCES visitors(id)
        );
        """
    )
    conn.commit()

    cur = conn.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        from werkzeug.security import generate_password_hash

        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", generate_password_hash("admin123"), "admin"),
        )
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("staff", generate_password_hash("staff123"), "staff"),
        )
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("student", generate_password_hash("student123"), "student"),
        )
        conn.commit()
    conn.close()


def dict_row(row):
    return {k: row[k] for k in row.keys()}


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        from werkzeug.security import check_password_hash

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        role = request.form.get("role", "staff")

        if role == "admin":
            return render_template("signup.html", error="Admin accounts cannot be self-created")
        if not username or not password:
            return render_template("signup.html", error="Username and password are required")
        if password != confirm:
            return render_template("signup.html", error="Passwords do not match")
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters")

        from werkzeug.security import generate_password_hash

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), role),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("signup.html", error="Username already exists")
        conn.close()
        return redirect(url_for("login"))
    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    total_today = conn.execute(
        "SELECT COUNT(*) FROM visitors WHERE date(entry_time) = ?", (today,)
    ).fetchone()[0]
    active_visitors = conn.execute(
        "SELECT COUNT(*) FROM visitors WHERE exit_time IS NULL"
    ).fetchone()[0]
    active_passes = conn.execute(
        "SELECT COUNT(*) FROM gatepasses WHERE status = 'active'"
    ).fetchone()[0]
    recent_visitors = conn.execute(
        "SELECT * FROM visitors ORDER BY id DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        total_today=total_today,
        active_visitors=active_visitors,
        active_passes=active_passes,
        recent_visitors=[dict_row(r) for r in recent_visitors],
    )


@app.route("/visitors")
def visitors():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM visitors ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template(
        "visitor.html",
        visitors=[dict_row(r) for r in rows],
        username=session["username"],
        role=session["role"],
    )


@app.route("/gatepass")
def gatepass():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    passes = conn.execute(
        """
        SELECT g.*, v.full_name as visitor_name
        FROM gatepasses g
        JOIN visitors v ON g.visitor_id = v.id
        ORDER BY g.id DESC
        """
    ).fetchall()
    visitors = conn.execute(
        "SELECT id, full_name FROM visitors ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template(
        "gatepass.html",
        passes=[dict_row(r) for r in passes],
        visitors=[dict_row(r) for r in visitors],
        username=session["username"],
        role=session["role"],
    )


@app.route("/api/visitors", methods=["GET", "POST"])
def api_visitors():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "POST":
        data = request.get_json()
        full_name = data.get("full_name", "")
        phone = data.get("phone", "")
        email = data.get("email", "")
        address = data.get("address", "")
        company = data.get("company", "")
        purpose = data.get("purpose", "")
        vehicle_number = data.get("vehicle_number", "")
        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db()
        cur = conn.execute(
            """
            INSERT INTO visitors
                (full_name, phone, email, address, company, purpose,
                 vehicle_number, entry_time, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (full_name, phone, email, address, company, purpose,
             vehicle_number, entry_time, session["user_id"]),
        )
        conn.commit()
        visitor_id = cur.lastrowid
        conn.close()
        return jsonify({"id": visitor_id, "message": "Visitor added successfully"}), 201

    if request.method == "GET":
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM visitors ORDER BY id DESC"
        ).fetchall()
        conn.close()
        return jsonify({"visitors": [dict_row(r) for r in rows]})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
