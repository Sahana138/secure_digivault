# file: database/models.py

from database.db import db
from datetime import datetime

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    face_encoding = db.Column(db.PickleType)

    failed_attempts = db.Column(db.Integer, default=0)

    locked = db.Column(db.Boolean, default=False)

    lock_time = db.Column(db.DateTime, nullable=True)