from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()

@app.route("/", methods=["GET","POST"])
def index():

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    if request.method == "POST":

        date = request.form["date"]
        category = request.form["category"]
        amount = request.form["amount"]
        desc = request.form["desc"]

        cursor.execute(
        "INSERT INTO expenses(date,category,amount,description) VALUES(?,?,?,?)",
        (date,category,amount,desc))

        conn.commit()

    cursor.execute("SELECT * FROM expenses")
    data = cursor.fetchall()

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    chart = cursor.fetchall()

    conn.close()

    categories = [row[0] for row in chart]
    amounts = [row[1] for row in chart]

    return render_template("index.html",
                           expenses=data,
                           categories=categories,
                           amounts=amounts)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)