from backend.database import connect_db
from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__, template_folder='.')
app.secret_key = "secret123"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root75",
    database="library_db"
)

cursor = db.cursor(dictionary=True)


@app.route('/', methods=['GET','POST'])
def login():

    error = None

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']

            if user['role'] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/student')
        else:
            error = "Invalid email or password"

    return render_template('login.html', error=error)

@app.route('/student')
def student():
    return render_template('student_dashboard.html')

@app.route('/admin')
def admin():
    return render_template('admin_dashboard.html')


@app.route('/apply_card', methods=['POST'])
def apply_card():

    user_id = session['user_id']

    cursor.execute(
        "INSERT INTO library_cards (user_id,status) VALUES (%s,'Pending')",
        (user_id,)
    )

    db.commit()

    return redirect('/student?applied=1')


@app.route('/books')
def books():

    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    return render_template('books.html', books=books)

@app.route('/admin/cards')
def admin_cards():

    cursor.execute("""
        SELECT library_cards.id, users.name, library_cards.status
        FROM library_cards
        JOIN users ON library_cards.user_id = users.id
    """)

    cards = cursor.fetchall()

    return render_template('admin_cards.html', cards=cards)

@app.route('/admin/book_approve/<int:req_id>')
def approve_book(req_id):

    cursor.execute(
        "UPDATE book_requests SET status='Approved' WHERE id=%s",
        (req_id,)
    )

    db.commit()

    return redirect('/admin/book_requests')

@app.route('/admin/book_reject/<int:req_id>')
def reject_book(req_id):

    cursor = db.cursor()

    cursor.execute(
        "UPDATE book_requests SET status='Declined' WHERE id=%s",
        (req_id,)
    )

    db.commit()

    return redirect('/admin/book_requests')


@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cursor.execute(
            "INSERT INTO users(name,email,password,role) VALUES(%s,%s,%s,'user')",
            (name,email,password)
        )

        db.commit()

        return redirect('/')

    return render_template('register.html')

@app.route('/request/<int:book_id>')
def request_book(book_id):

    user_id = session.get('user_id')

    cursor.execute(
        "INSERT INTO book_requests(user_id,book_id,status) VALUES(%s,%s,'Pending')",
        (user_id, book_id)
    )

    db.commit()

    return redirect('/books?success=1')

@app.route('/admin/book_requests')
def admin_book_requests():

    cursor.execute("""
        SELECT book_requests.id, users.name, books.title, book_requests.status
        FROM book_requests
        JOIN users ON book_requests.user_id = users.id
        JOIN books ON book_requests.book_id = books.id
    """)

    requests = cursor.fetchall()

    return render_template('admin_book_requests.html', requests=requests)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
