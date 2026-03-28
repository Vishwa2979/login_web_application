from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

USERS_FILE = "users.json"


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please fill in all fields.", "error")
            return render_template("login.html")

        users = load_users()

        if username not in users:
            flash("Account not found. Please register first.", "error")
            return render_template("login.html")

        if users[username] != hash_password(password):
            flash("Incorrect password. Please try again.", "error")
            return render_template("login.html")

        session["username"] = username
        flash(f"Welcome back, {username}! You have logged in successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm  = request.form.get("confirm", "").strip()

        if not username or not password or not confirm:
            flash("Please fill in all fields.", "error")
            return render_template("register.html")

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        users = load_users()

        if username in users:
            flash("Username already exists. Please choose another.", "error")
            return render_template("register.html")

        users[username] = hash_password(password)
        save_users(users)

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
