import sqlite3
from flask import Flask, request

app = Flask(__name__)
conn = sqlite3.connect("users_flawed.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    cursor.execute(
        f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    )
    conn.commit()
    return "User registered"


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    cursor.execute(
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    )
    user = cursor.fetchone()
    if user:
        return "Login successful"
    return "Login failed"


@app.route("/delete_user/<int:id>")
def delete_user(id):
    cursor.execute(f"DELETE FROM users WHERE id = {id}")
    conn.commit()
    return "User deleted"


if __name__ == "__main__":
    app.run()
