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
db = SQLAlchemy(app)

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
def load_user():
    return None

#user class
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False


#main page
@app.route('/')
def index():
    return render_template('index.html')

#register

#login

#logout

#show user's subscriptions

#show all subsciptions

#cancel a subsciprtion

#add a subsciption


if __name__ =='__main__':
    app.run(debug=True)