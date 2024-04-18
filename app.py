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
app.config['SQLALCHEMY_BINDS'] = {
        'db2': 'sqlite:///subs.db',
        'db3': 'sqlite:///store.db'
}
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
def load_user(user_id):
    return Users.query.get(user_id)

#user class
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    #notification = db.Column(db.Integer, default=0)

#subscription class
class Subscriptions(db.Model):
    __bind_key__='db2'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    price = db.Column(db.DECIMAL(6,2), nullable=False)

class Store(db.Model):
    __bind_key__='db3'
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer)
    sub_id =db.Column(db.Integer)

#main page
@app.route('/')
def index():
    subs=[]
    ids=[a.id for a in Subscriptions.query.all()]
    if current_user.is_authenticated:
        username=Users.query.filter_by(id=current_user.id).first().username
        subids = [a.sub_id for a in Store.query.filter_by(user_id=current_user.id).all()]
        for i in ids:
            if(i not in subids):
                subscription=Subscriptions.query.filter_by(id=i).first()
                if subscription.price < 10.00:
                    subs.append(subscription)
        return render_template('index.html',username=username, subs=subs)
    else:
        username="Friend"
        for i in ids:
            subscription=Subscriptions.query.filter_by(id=i).first()
            if subscription.price < 10.00:
                subs.append(subscription)
        return render_template('index.html',username=username, subs=subs)

#register
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        email=request.form['email']
        password=request.form['password']
        c_password=request.form['confirm_password']
        #notification=request.form['notification']

        user=Users.query.filter_by(email=email).first()
        
        if not is_password_strong(password):
            flash('Password is not strong enough!','error')
        elif password != c_password:
            flash('Passwords do not match!','error')
        elif user != None:
            flash('User already exists!','error')
        else:
            hash_password=generate_password_hash(password)
            #insert into database
            user = Users(username=username,email=email,password=hash_password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!','success')
            login_user(user, remember=True)
            ids=[a.id for a in Subscriptions.query.all()]
            subs=[]
            for i in ids:
                subscription=Subscriptions.query.filter_by(id=i).first()
                if subscription.price < 10.00:
                    subs.append(subscription)
            return render_template('index.html',username=username, subs=subs)
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
    flash('Logged out successfully!','success')
    return redirect(url_for("index"))

#show user's subscriptions
@app.route("/mysubscriptions")
@login_required
def mysubscriptions():
    subids = [a.sub_id for a in Store.query.filter_by(user_id=current_user.id).all()]
    subs=[]
    count = 0
    total = 0
    for i in subids:
        subscription = Subscriptions.query.filter_by(id=i).first()
        if subscription:
            subs.append(subscription)
            count += 1
            total += subscription.price
    return render_template('mysubscriptions.html',subs=subs, count=count, total=total)

#show all subsciptions
@app.route("/subscriptions")
def subscriptions():
    subs=[]
    if current_user.is_authenticated:
        subids = [a.sub_id for a in Store.query.filter_by(user_id=current_user.id).all()]
        ids=[a.id for a in Subscriptions.query.all()]
        for i in ids:
            if(i not in subids):
                subscription=Subscriptions.query.filter_by(id=i).first()
                if subscription:
                    subs.append(subscription)
    else:
        subs=list(Subscriptions.query.all())
    return render_template('subscriptions.html',subs=subs)

#cancel a subsciprtion
@app.route("/<string:id>/delete", methods=['POST'])
@login_required
def delete(id):
    if request.method == 'POST':
        #delete the subsciption
        s=Store.query.filter_by(sub_id=id).first()
        db.session.delete(s)
        db.session.commit()
        flash("Subscription deleted successfully!")
        return redirect(url_for('mysubscriptions'))
    return redirect(url_for('index'))

#add a subsciption
@app.route("/<string:id>/subscribe",methods=['POST'])
@login_required
def subscribe(id):
    if request.method=='POST':
        #add subscription
        s = Store(user_id=current_user.id,sub_id=id)
        db.session.add(s)
        db.session.commit()
        flash("Subscription added!")
        return redirect(url_for('mysubscriptions'))
    return render_template('subscriptions.html')

#password strength check
def is_password_strong(password):
    # Minimum 8 characters, at least one uppercase letter, one lowercase letter, one number, and one special character
    pattern = r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}'
    return re.match(pattern, password) is not None

if __name__ =='__main__':
    app.run(debug=True)