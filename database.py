# AI DISCLOSURE:
# AI tools were used for syntax guidance. Logic and structure are my own.

import sqlite3

DB_NAME = "finance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            description TEXT,
            amount REAL,
            category TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_transactions(df, user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO transactions (user_id, date, description, amount, category)
            VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            row["Date"],
            row["Description"],
            row["Amount"],
            row["Category"]
        ))

    conn.commit()
    conn.close()


def fetch_summary(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = ? AND amount > 0",
        (user_id,)
    )
    income = cur.fetchone()[0] or 0

    cur.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = ? AND amount < 0",
        (user_id,)
    )
    expense = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE user_id = ? AND amount < 0
        GROUP BY category
    """, (user_id,))
    rows = cur.fetchall()

    conn.close()
    return income, expense, rows
