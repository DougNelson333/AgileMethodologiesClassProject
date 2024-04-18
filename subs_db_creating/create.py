from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from app import Subscriptions

# DONT RUN THIS UNLESS 'subs.db' IS EMPTY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_BINDS'] = {
        'db2': 'sqlite:///subs.db'
}
db = SQLAlchemy(app)

with app.app_context():
    file = open("subs.txt","r")
    line = file.readline()
    while(line!= ""):
        name = line.split(",")[0].strip()
        category=line.split(",")[1].strip()
        price = line.split(",")[2].strip()
        subs = Subscriptions(name=name,category=category,price=float(price))
        db.session.add(subs)
        db.session.commit()
        line = file.readline()

    file.close()

