from flask import Flask, render_template, request, redirect, flash, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy #pylint: disable=import-error
from flask_migrate import Migrate #pylint: disable=import-error
from sqlalchemy.sql import func #pylint: disable=import-error
import re

app = Flask(__name__)
app.secret_key = "fSD;fkljsf;ldskfjSD:GLiwougerafvbcv872t3riwegDSklfJHD"
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dojo_tweets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

likes_table = db.Table('likes', 
db.Column('tweet_id', db.ForeignKey('tweets.id'), primary_key=True), 
db.Column('user_id', db.ForeignKey('users.id'), primary_key=True))
db.Column('created_at', db.DateTime, server_default=func.now())

followers_table=db.Table('followers',
    db.Column("follower_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("created_at", db.DateTime, server_default=func.now())
)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    liked_tweets = db.relationship("Tweet", secondary=likes_table)
    followers = db.relationship("User",
        secondary=followers_table,
        primaryjoin=id==followers_table.c.followed_id,
        secondaryjoin=id==followers_table.c.follower_id,
        backref="following")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def add_new_user(cls, data):
        new_user = cls(first_name=data['first_name'], 
                        last_name=['last_name'], 
                        email=data['email'],
                        password_hash=bcrypt.generate_password_hash(data['password'])
                        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def find_registration_errors(cls, form_data):
        errors=[]
        if len(form_data['first_name']) < 1:
            errors.append("first name must be at least 1 character long")
        if len(form_data['last_name']) < 1:
            errors.append("last name must be at least 1 character long")
        if not EMAIL_REGEX.match(form_data['email']):
            errors.append("invalid email")
        if form_data['password'] != request.form['confirm']:
            errors.append("passwords dont match")
        if len(form_data['password']) < 8:
            errors.append("password isn't long enough")
        return errors

    @classmethod
    def register_new_user(cls, form_data):
        errors = cls.find_registration_errors(form_data)
        valid = len(errors)==0
        data = cls.add_new_user(form_data) if valid else errors
        return {
            "status": "good" if valid else "bad",
            "data": data
        }
    

class Tweet(db.Model):
    __tablename__ = "tweets"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship("User", backref="tweets", cascade="all")
    likers = db.relationship("User", secondary=likes_table)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def add_new_tweet(cls, tweet):
        db.session.add(tweet)
        db.session.commit()
        return tweet

    def age(self):
        age = self.created_at
        return age

class Follow(db.Model):
    __tablename__="follows"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user1 = db.relationship("User", backref="likes", cascade="all")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user2 = db.relationship("User", backref="likes", cascade="all")
    created_at=db.Column(db.DateTime, server_default=func.now())


# other utilities 
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
strongRegex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})")

@app.route('/')
def index():
    return render_template("login_reg.html")

@app.route("/register", methods=["POST"])
def register():
    #create new user based off form data
    result=User.register_new_user(request.form)
    #validations for good and bad status based off given information
    if result['status']=="good":
        user=result['data']
        session['cur_user'] = {
            "first": user.first_name,
            "last": user.last_name,
            "id": user.id
        }
        return redirect("/success")
    else:
        #if not good data, return flash errors and redirect to login
        errors=result['data']
        for error in errors:
            flash(error)
        return redirect("/")

@app.route('/success')
def tweet_landing():
    if 'cur_user' not in session:
        flash("Please log in")
        return redirect('/')
    
    #get id from current session user
    cur_user=User.query.get(session['cur_user']['id'])
    #make list of tweets from followed users and current user
    approved_users_ids = [user.id for user in cur_user.following] + [cur_user.id]
    #filter tweets from followed and current
    all_tweets = Tweet.query.filter(Tweet.author_id.in_(approved_users_ids)).all()
    return render_template('tweet_landing.html', tweets=all_tweets)
   
@app.route("/login", methods=['POST'])
def login():
    user=User.query.filter_by(email=request.form['email']).all()
    valid = True if len(user)==1 and bcrypt.check_password_hash(user[0].password_hash, request.form['password']) else False
    if valid:
        session['cur_user'] = {
            "first": user.first_name,
            "last": user.last_name,
            "id": user.id
        }
        return redirect("/twitter")
    else:
        flash("Invalid login credentials")
        return redirect("/")

@app.route("/tweet", methods=["POST"])
def add_tweet():
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    new_tweet=Tweet(
        message=request.form['tweet'],
        author_id=int(session['cur_user']['id'])
    )
    if len(new_tweet.message) > 0:
        Tweet.add_new_tweet(new_tweet)
    else:
        flash("need more tweet length yo!")
    return redirect("/twitter")

@app.route("/tweets/<tweet_id>/delete", methods=['POST'])
def delete_tweet(tweet_id):
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    tweet_being_deleted=Tweet.query.get(tweet_id)
    tweets_author=tweet_being_deleted.author
    tweets_author.tweets.remove(tweet_being_deleted)
    db.session.commit()
    return redirect("/twitter")

@app.route("/tweets/<tweet_id>/like", methods=["POST"])
def add_like(tweet_id):
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    liked_tweet=Tweet.query.get(tweet_id)
    liker=User.query.get(session['cur_user']['id'])
    liker.liked_tweets.append(liked_tweet)
    db.session.commit()
    return redirect("/twitter")

@app.route("/tweets/<tweet_id>/edit")
def show_edit(tweet_id):
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    tweet=Tweet.query.get(tweet_id)
    return render_template("edit.html", tweet=tweet)

@app.route("/tweets/<tweet_id>/update", methods=["POST"])
def update_tweet(tweet_id):
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    tweet=Tweet.query.get(tweet_id)
    if len(request.form['tweet'])>0:
        tweet.message=request.form['tweet']
        db.session.commit()
        return redirect("/twitter")
    else:
        flash("need more tweet!")
        return render_template("edit.html", tweet=tweet)

@app.route("/users")
def show_users():
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    users_list=User.query.all()
    return render_template("users.html", users=users_list)

@app.route("/follow/<user_id>")
def follow_user(user_id):
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    logged_in_user=User.query.get(session['cur_user']['id'])
    followed_user=User.query.get(user_id)
    followed_user.followers.append(logged_in_user)
    db.session.commit()
    return redirect("/users")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__  == "__main__":
    app.run(debug=True)