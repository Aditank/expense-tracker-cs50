from flask import Flask, render_template, request, redirect, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import sqlite3

from database import init_db, insert_transactions, fetch_summary
from categorizer import categorize_transaction
from analysis import summary_dataframe

app = Flask(__name__)
app.secret_key = "cs50-final-project-key"

init_db()

def login_required(route):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return route(*args, **kwargs)
    wrapper.__name__ = route.__name__
    return wrapper


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hash_pw = generate_password_hash(password)

        conn = sqlite3.connect("finance.db")
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hash_pw)
            )
            conn.commit()
        except:
            conn.close()
            return "Username already exists"
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("finance.db")
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,)
        )
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/")
        return "Invalid credentials"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        file = request.files["file"]
        df = pd.read_csv(file)

        df["Category"] = df["Description"].apply(categorize_transaction)

        insert_transactions(df, session["user_id"])

        income, expense, rows = fetch_summary(session["user_id"])
        summary_df = summary_dataframe(rows)

        with pd.ExcelWriter("expense_report.xlsx") as writer:
            df.to_excel(writer, index=False, sheet_name="Transactions")
            summary_df.to_excel(writer, index=False, sheet_name="Summary")

        return render_template(
            "result.html",
            income=income,
            expense=expense,
            table=summary_df.to_html(index=False)
        )

    return render_template("index.html")


@app.route("/download")
@login_required
def download():
    return send_file("expense_report.xlsx", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
