from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import jwt
import datetime
import bcrypt
from functools import wraps

from getPhoneNumber import GetNumbers
from getAgent import GetAgents
from getAllCalls import GetCalls

app = Flask(__name__)
api = Api(app)

# Secret key for JWT
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with env var in production

# In-memory user store (replace with DB)
users = {
    "admin": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
}

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

    username = auth_data.get('username')
    password = auth_data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    stored_password = users.get(username)

    if stored_password and bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401


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
api.add_resource(AuthGetNumbers, '/get-numbers')
api.add_resource(AuthGetAgents, '/get-agents')
api.add_resource(AuthGetCalls, '/get-calls')

if __name__ == "__main__":
    app.run(debug=True)
