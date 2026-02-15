from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from urllib.parse import urlparse

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "secret123"


def connect():
    database_url = os.getenv("MYSQL_PUBLIC_URL")

    if not database_url:
        raise ValueError("MYSQL_PUBLIC_URL not set")

    url = urlparse(database_url)

    return mysql.connector.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        port=url.port,
        database=url.path[1:]
    )


# ---------------- LOGIN ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        conn = connect()
        cursor = conn.cursor(dictionary=True)

        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect("/admin")
            return redirect("/student")

        error = "Invalid login"

    return render_template("login.html", error=error)


# ---------------- STUDENT ---------------- #

@app.route("/student")
def student():
    return render_template("student_dashboard.html")


@app.route("/apply_card", methods=["POST"])
def apply_card():
    if "user_id" not in session:
        return redirect("/")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO library_cards (user_id, status) VALUES (%s, 'Pending')",
        (session["user_id"],)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/student?applied=1")


@app.route("/books")
def books():
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("books.html", books=books)


@app.route("/request/<int:book_id>")
def request_book(book_id):
    if "user_id" not in session:
        return redirect("/")

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO book_requests (user_id, book_id, status) VALUES (%s, %s, 'Pending')",
        (session["user_id"], book_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/books")


# ---------------- ADMIN ---------------- #

@app.route("/admin")
def admin():
    return render_template("admin_dashboard.html")


@app.route("/admin/cards")
def admin_cards():
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT library_cards.id, users.name, library_cards.status
        FROM library_cards
        JOIN users ON library_cards.user_id = users.id
    """)

    cards = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_cards.html", cards=cards)


@app.route("/admin/approve_card/<int:id>")
def approve_card(id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE library_cards SET status='Approved' WHERE id=%s",
        (id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/cards")


@app.route("/admin/decline_card/<int:id>")
def decline_card(id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE library_cards SET status='Declined' WHERE id=%s",
        (id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/cards")


@app.route("/admin/book_requests")
def admin_book_requests():
    conn = connect()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT book_requests.id, users.name, books.title, book_requests.status
        FROM book_requests
        JOIN users ON book_requests.user_id = users.id
        JOIN books ON book_requests.book_id = books.id
    """)

    requests = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_book_requests.html", requests=requests)


@app.route("/admin/book_approve/<int:id>")
def approve_book(id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE book_requests SET status='Approved' WHERE id=%s",
        (id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/book_requests")


@app.route("/admin/book_reject/<int:id>")
def reject_book(id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE book_requests SET status='Declined' WHERE id=%s",
        (id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/book_requests")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = connect()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'user')",
            (request.form["name"], request.form["email"], request.form["password"])
        )

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
