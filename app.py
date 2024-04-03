from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user,login_required, logout_user, current_user
from datetime import timedelta
from werkzeug.exceptions import abort
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)

#database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy()

#configurations
app.config['SECRET_KEY']= 'your secret key'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE']=True
app.config['SESSION_COOKIE_HTTPONLY']=True

#login management
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#login manager user load from database
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

#user class
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

db.init_app(app)

#main page
@app.route('/')
def index():
    return render_template('index.html')

#register
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        c_password=request.form['confirm_password']

        user=Users.query.filter_by(email=email).first()
        
        if not is_password_strong(password):
            flash('Password is not strong enough!','error')
        elif password != c_password:
            flash('Passwords do not match!','error')
        elif user != None:
            flash('User already exists!','error')
        else:
            hash_password=generate_password_hash(password)
            #insert database
            user = Users(username=username,email=email,password=hash_password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!','success')
            return render_template('index.html')
    return render_template('register.html')

#login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user,remember=True)
            flash('Login successful!','success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!','error')
            return redirect(url_for('login'))
    return render_template('login.html')

#logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

#show user's subscriptions
@app.route("/userlist")
@login_required
def userlist():
    usersubs = None
    return render_template('userlist.html',usersubs=usersubs)

#show all subsciptions
@app.route("/list")
def list():
    subs=None
    return render_template('list.html',subs=subs)

#cancel a subsciprtion
@app.route("/delete", methods=['POST'])
@login_required
def delete():
    if request.method == 'POST':
        #delete the subsciption
        flash("Subscription deleted successfully!")
        return redirect(url_for('userlist'))
    return redirect(url_for('index'))

#add a subsciption
@app.route("/add",methods=['GET','POST'])
@login_required
def add():
    if request.method=='POST':
        #add subscription
        flash("Subscription added!")
        return redirect(url_for('userlist'))
    return render_template('list.html')

#password strength check
def is_password_strong(password):
    # Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number, and one special character
    pattern = r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}'
    return re.match(pattern, password) is not None

if __name__ =='__main__':
    app.run(debug=True)