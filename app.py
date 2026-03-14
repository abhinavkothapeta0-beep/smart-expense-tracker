from flask import Flask, render_template, request, redirect, Response
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

def init_db():
    # Delete old database if exists
    if os.path.exists("expenses.db"):
        os.remove("expenses.db")
    
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Database created successfully!")

init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        date = request.form.get("date", today)
        
        cursor.execute(
            "INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)",
            (category, amount, date)
        )
        conn.commit()
        conn.close()
        return redirect("/")
    
    cursor.execute("SELECT id, category, amount, date FROM expenses ORDER BY id DESC")
    data = cursor.fetchall()
    conn.close()
    
    print(f"DEBUG: Fetched {len(data)} rows")  # Debug line
    return render_template("index.html", data=data, today=today)

@app.route("/chart")
def chart():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    categories = [row[0] for row in data]
    amounts = [float(row[1]) for row in data]
    conn.close()
    return render_template("chart.html", categories=categories, amounts=amounts)

@app.route("/monthly")
def monthly():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(amount)
        FROM expenses GROUP BY month ORDER BY month
    """)
    data = cursor.fetchall()
    months = [row[0] or 'Unknown' for row in data]
    totals = [float(row[1] or 0) for row in data]
    conn.close()
    return render_template("monthly.html", months=months, totals=totals)

@app.route("/insights")
def insights():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, SUM(amount) FROM expenses 
        GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1
    """)
    top = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM expenses")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = float(cursor.fetchone()[0] or 0)
    conn.close()
    
    message = f"Total: ₹{total:.2f} | Records: {count}"
    if top:
        message += f" | Top: {top[0]} (₹{top[1]:.2f})"
    
    return render_template("insights.html", message=message)

@app.route("/download")
def download():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, amount, date FROM expenses ORDER BY date DESC")
    data = cursor.fetchall()
    conn.close()
    
    def generate():
        yield "ID,Category,Amount,Date\n"
        for row in data:
            yield f"{row[0]},{row[1]},{row[2]:.2f},{row[3]}\n"
    
    return Response(generate(), mimetype="text/csv", 
                   headers={"Content-Disposition": "attachment; filename=expenses.csv"})

if __name__ == "__main__":
    app.run(debug=True)
