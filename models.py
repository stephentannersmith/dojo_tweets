from config import db, func, re, bcrypt, EMAIL_REGEX, strongRegex, request

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


likes_table = db.Table('likes', 
db.Column('tweet_id', db.ForeignKey('tweets.id'), primary_key=True), 
db.Column('user_id', db.ForeignKey('users.id'), primary_key=True))
db.Column('created_at', db.DateTime, server_default=func.now())

followers_table=db.Table('followers',
db.Column("follower_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
db.Column("followed_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
db.Column("created_at", db.DateTime, server_default=func.now())
)