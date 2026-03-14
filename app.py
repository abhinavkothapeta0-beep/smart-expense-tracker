from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

DB_NAME = "expenses.db"


# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()


# Create table when app starts
init_db()


# ---------- HOME ----------
@app.route("/")
def index():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
    expenses = cursor.fetchall()

    conn.close()

    return render_template("index.html", expenses=expenses)


# ---------- ADD EXPENSE ----------
@app.route("/add", methods=["POST"])
def add():
    date = request.form["date"]
    category = request.form["category"]
    amount = request.form["amount"]
    description = request.form["description"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
        (date, category, amount, description)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------- DELETE ----------
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


# ---------- RUN LOCAL ----------
if __name__ == "__main__":
    app.run(debug=True)
