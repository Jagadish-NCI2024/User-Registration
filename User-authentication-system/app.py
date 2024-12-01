from flask import Flask, flash, request,render_template, redirect,session, make_response, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
 

    def __init__(self,email,password,name):
        self.name = name        
        self.password = password
        self.email = email
    
    def check_password(self,password):
         return password
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        resp = make_response(redirect(url_for('login')))
        resp.set_cookie('secureCookie', email, secure=True, httponly=True, samesite='Strict', max_age=60*60*24)
        
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html',user=user)
    
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        
        # Delete the user from the database
        db.session.delete(user)
        db.session.commit()

        # Clear the session and redirect to login
        session.pop('email', None)
        flash('Your account has been deleted successfully.', 'success')
        return redirect('/login')
    
    return redirect('/login')
@app.route('/post', methods=['GET', 'POST'])
def post_message():
    user = request.cookies.get('user')
    if not user:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    if request.method == 'POST':
        message = request.form.get('message', '')
        # Reflecting the message directly (vulnerable to XSS)
        return render_template('dashboard.html', user=user, message=message)

    return render_template('dashboard.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)