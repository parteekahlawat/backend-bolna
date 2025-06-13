from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db
from models.user import User
from models.content import Content
import jwt
import datetime
import bcrypt
from functools import wraps

from flask_restful import Resource, Api
from getPhoneNumber import GetNumbers
from getAgent import GetAgents
from getAllCalls import GetCalls
app = Flask(__name__)

# Enable CORS globally
CORS(app)
api = Api(app)

# Init DB

# Secret key for JWT
# Config
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with env var in production
# app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


    
# Token-required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            token = token.replace("Bearer ", "")
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user = data['username']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated


# Login Route
@app.route('/login', methods=['POST'])
def login():
    auth_data = request.get_json()

    # username = auth_data.get('username')
    email = auth_data.get('email')
    password = auth_data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if not email or not password:
        return jsonify({"error": "Missing username or password"}), 400

    stored_password = user.hashed_password

    if stored_password and bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        token = jwt.encode({
            'username': user.username,
            'email': email,
            'agent_id': user.agent_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401

# Register Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    agent_id = data.get('agent_id')

    if not username or not email or not password or not agent_id:
        return jsonify({"error": "Missing required fields"}), 400

    existing_user = User.query.filter(User.email == email).first()

    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        agent_id=agent_id
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

# @token_required
@app.route('/add-content', methods=['POST'])
def add_content():
    data = request.get_json()

    content = Content(
        agent_id=data.get('agent_id'),
        name=data.get('name'),
        phone_number=data.get('phone_number'),
        summary=data.get('summary'),
        transcript=data.get('transcript'),
        link=data.get('link'),
        to_number=data.get('to_number'),
        cost=data.get('cost')
    )

    db.session.add(content)
    db.session.commit()

    return jsonify({"message": "Content added successfully!"}), 201

# @token_required
@app.route('/get-content', methods=['GET'])
def get_content():
    contents = Content.query.all()
    result = []

    for c in contents:
        result.append({
            "id": c.id,
            "agent_id": c.agent_id,
            "name": c.name,
            "phone_number": c.phone_number,
            "summary": c.summary,
            "transcript": c.transcript,
            "link": c.link,
            "to_number": c.to_number,
            "cost": c.cost
        })

    return jsonify(result), 200

# Secure wrappers for each resource
class AuthGetNumbers(GetNumbers):
    @token_required
    def get(self):
        return super().get()

class AuthGetAgents(GetAgents):
    @token_required
    def get(self):
        return super().get()

class AuthGetCalls(GetCalls):
    @token_required
    def post(self):
        return super().post()


# API routes
# api.add_resource(AuthGetNumbers, '/get-numbers')
# api.add_resource(AuthGetAgents, '/get-agents')
# api.add_resource(AuthGetCalls, '/get-calls')

api.add_resource(GetNumbers, '/get-numbers')
api.add_resource(GetAgents, '/get-agents')
api.add_resource(GetCalls, '/get-calls')

with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True)
