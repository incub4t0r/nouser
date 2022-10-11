from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import timedelta
import secrets


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nouser.db'
app.config['SECRET_KEY'] = 'thisissecret'
db = SQLAlchemy(app)
ROOT = os.path.dirname(os.path.realpath(__file__))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    # crawls = db.Column(db.Integer)
    crawls = db.relationship("Crawl")

    def __repr__(self):
        return f"User('{self.id}')"


class Crawl(db.Model):
    __tablename__ = 'crawls'
    id = db.Column(db.Integer, primary_key=True)
    crawl_id = db.Column(db.String)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Crawl('{self.id}')"


def db_check():
    if not os.path.exists(os.path.join(ROOT, 'instance', 'nouser.db')):
        print("creating database...")
        with app.app_context():
            db.create_all()
            return
    print("database already exists")


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=31)


@app.route('/', methods=['GET'])
def index():
    if 'id' in session:
        print(
            f"db status: {db.session.query(User).filter_by(id=session['id']).first()}")
        if db.session.query(User).filter_by(id=session['id']).first() is not None:
            return render_template('index.html', msg="You have a session ready to go")
        else:
            return render_template('index.html', msg="You have a session but no user wtf happened")
    else:
        session['id'] = secrets.token_hex(16)
        db.session.add(User(id=session['id']))
        db.session.commit()
    return render_template('index.html', msg="You have started a session")


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        user = User(id=session['id'])
        crawl_id = request.form['crawl_id']
        db.session.add(Crawl(user_id=user.id, crawl_id=crawl_id))
        db.session.commit()
        print(user)
        return redirect(url_for('index'))
    return render_template('new.html')


@app.route('/list', methods=['GET'])
def list():
    user = User(id=session['id'])
    crawls = Crawl.query.filter_by(user_id=user.id).all()
    return render_template('list.html', crawls=crawls)


if __name__ == '__main__':
    db_check()
    app.run(debug=True)
