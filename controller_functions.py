from flask import render_template, redirect, request, session, flash
from config import db, bcrypt
from models import User, Tweet, Follow

def index():
    return render_template("login_reg.html")

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

def delete_tweet(tweet_id):
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    tweet_being_deleted=Tweet.query.get(tweet_id)
    tweets_author=tweet_being_deleted.author
    tweets_author.tweets.remove(tweet_being_deleted)
    db.session.commit()
    return redirect("/twitter")

def add_like(tweet_id):
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    liked_tweet=Tweet.query.get(tweet_id)
    liker=User.query.get(session['cur_user']['id'])
    liker.liked_tweets.append(liked_tweet)
    db.session.commit()
    return redirect("/twitter")

def show_edit(tweet_id):
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    tweet=Tweet.query.get(tweet_id)
    return render_template("edit.html", tweet=tweet)

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

def show_users():
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    users_list=User.query.all()
    return render_template("users.html", users=users_list)

def follow_user(user_id):
    if "cur_user" not in session:
        flash("Please Log In")
        return redirect("/")
    logged_in_user=User.query.get(session['cur_user']['id'])
    followed_user=User.query.get(user_id)
    followed_user.followers.append(logged_in_user)
    db.session.commit()
    return redirect("/users")

def logout():
    session.clear()
    return redirect("/")