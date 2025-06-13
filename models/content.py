from . import db

class Content(db.Model):
    __tablename__ = 'content' 
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(150))
    phone_number = db.Column(db.String(50))
    summary = db.Column(db.Text)
    transcript = db.Column(db.Text)
    link = db.Column(db.String(300))
    to_number = db.Column(db.String(50))
    cost = db.Column(db.Float)
