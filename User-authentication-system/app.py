from flask import Flask, flash, request, render_template, redirect, session, make_response, url_for, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'
DATABASE = 'database.db'

# Function to connect to the SQLite database
def create_table():
    conn = sqlite3.connect(DATABASE)  # Use the correct database ('database.db')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

# Drop the table if it exists
    cursor.execute("DROP TABLE IF EXISTS User")

# Recreate the table with the correct schema
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    comments TEXT
      )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        with get_db() as db:
            db.execute('INSERT INTO User (name, email,password) VALUES ("{}", "{}", "{}")'.format(name, email, password))

            db.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with get_db() as db:
            user = db.execute('SELECT * FROM User WHERE email = ?', (email,)).fetchone()

        if user and user['password'] == password:
            session['email'] = user['email']
            resp = make_response(redirect('/dashboard'))
            resp.set_cookie('secureCookie', email, secure=True, httponly=True, samesite='Strict', max_age=60*60*24)
            return resp
        else:
            return render_template('login.html', error='Invalid user')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        with get_db() as db:
            user = db.execute('SELECT * FROM User WHERE email = ?', (session['email'],)).fetchone()
        return render_template('dashboard.html', user=user)

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'email' in session:
        with get_db() as db:
            db.execute('DELETE FROM User WHERE email = ?', (session['email'],))
            db.commit()

        session.pop('email', None)
        flash('Your account has been deleted successfully.', 'success')
        return redirect('/login')

    return redirect('/login')


@app.route('/post', methods=['GET', 'POST'])
def post_message():
    if 'email' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user_email = session['email']

    if request.method == 'POST':
      message = request.form.get('message', '')
       
      return render_template('dashboard.html', user=user_email, message=message)

    return render_template('dashboard.html', user=user_email)


# Function to get a database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()


if __name__ == '__main__':
    create_table()  # Ensure the table is created when starting the app
    app.run(debug=True)
