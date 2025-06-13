from . import db

class User(db.Model):
    __tablename__ = 'users' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)
    agent_id = db.Column(db.String(100), nullable=False)
