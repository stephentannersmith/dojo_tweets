from flask import Flask, render_template, request, redirect, flash, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy #pylint: disable=import-error
from flask_migrate import Migrate #pylint: disable=import-error
from sqlalchemy.sql import func #pylint: disable=import-error
import re

app = Flask(__name__)
app.secret_key = "fSD;fkljsf;ldskfjSD:GLiwougerafvbcv872t3riwegDSklfJHD"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dojo_tweets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
strongRegex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#\$%\^&\*])(?=.{8,})")