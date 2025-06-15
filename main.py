from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
import datetime
from config import Config
from database import (
    store_user, get_user, get_user_by_email, store_calls, get_agent_calls,
    get_call_details, store_agent, get_agent, delete_agent,
    hash_password, verify_password, users_collection, generate_user_id
)

app = Flask(__name__)
# Configure CORS to allow all origins, methods, and headers
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        # "allow_headers": ["Content-Type", "Authorization"]
    }
})

# JWT Configuration
app.config['SECRET_KEY'] = Config.SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = get_user(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token!'}), 401
        except:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = get_user(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token!'}), 401
            if current_user.get('role') != 'admin':
                return jsonify({'message': 'Admin privileges required!'}), 403
        except:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['company_name', 'email', 'firstname', 'lastname', 'password', 'agent_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate password strength
    if len(data['password']) < 7:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
    
    # Validate agent_id exists in agents collection
    # agent = get_agent(data['agent_id'])
    # if not agent:
    #     return jsonify({'error': 'Invalid agent_id'}), 400
    
    # Check if email already exists
    # existing_email = get_user_by_email(data['email'])
    # if existing_email:
    #     return jsonify({'error': 'Email already registered'}), 400
    
    # Generate unique user_id
    data['user_id'] = generate_user_id()
    # data['user_id'] = "user_1234567890"
    
    # Set default role as 'user'
    data['role'] = 'user'
    data['hashed_password'] = hash_password(data['password'])
    
    try:
        # store_user(data)
        
        # Generate JWT token with agent_ids
        token = jwt.encode({
            'user_id': data['user_id'],
            'role': data['role'],
            'agent_ids': [data['agent_id']],  # Include agent_ids in token
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'user_id': data['user_id'],
                'firstname': data['firstname'],
                'lastname': data['lastname'],
                'company_name': data['company_name'],
                'email': data['email'],
                'role': data['role']
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    # Get user by email
    user = get_user_by_email(data['email'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify password
    if not verify_password(user['hashed_password'], data['password']):
        return jsonify({'error': 'Invalid password'}), 401
    
    # Fetch user's agents
    agent_ids = user.get('agent_id', [])
    agents = []
    for agent_id in agent_ids:
        agent = get_agent(agent_id)
        if agent:
            agents.append(agent)
    
    # Generate JWT token with agent_ids
    token = jwt.encode({
        'user_id': user['user_id'],
        'role': user.get('role', 'user'),
        'agent_ids': agents,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, app.config['SECRET_KEY'])
    
    return jsonify({
        'token': token,
        'user': {
            'user_id': user['user_id'],
            'company_name': user['company_name'],
            'email': user['email'],
            'firstname': user['firstname'],
            'lastname': user['lastname'],
            'role': user.get('role', 'user'),
            # 'agents': agents
        }
    })

@app.route('/calls', methods=['POST'])
@token_required
def store_call_data(current_user):
    data = request.get_json()
    
    if not data or 'agent_id' not in data or 'calls_details' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate agent_id belongs to user
    if data['agent_id'] not in current_user.get('agent_id', []):
        return jsonify({'error': 'Unauthorized access to agent'}), 403
    
    try:
        store_calls(data['agent_id'], data['calls_details'])
        return jsonify({'message': 'Call data stored successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/calls/<agent_id>', methods=['GET'])
@token_required
def get_calls(current_user, agent_id):
    # Validate agent_id belongs to user
    if agent_id not in current_user.get('agent_id', []):
        return jsonify({'error': 'Unauthorized access to agent'}), 403
    
    calls = get_agent_calls(agent_id)
    if not calls:
        return jsonify({'error': 'No calls found'}), 404
    
    return jsonify(calls)

@app.route('/calls/<agent_id>/<to_number>', methods=['GET'])
@token_required
def get_call(current_user, agent_id, to_number):
    # Validate agent_id belongs to user
    if agent_id not in current_user.get('agent_id', []):
        return jsonify({'error': 'Unauthorized access to agent'}), 403
    
    call_details = get_call_details(agent_id, to_number)
    if not call_details:
        return jsonify({'error': 'Call not found'}), 404
    
    return jsonify(call_details)

@app.route('/agents', methods=['POST'])
@admin_required
def create_agent(current_user):
    data = request.get_json()
    
    if not data or 'agent_id' not in data or 'company_name' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if agent already exists
    existing_agent = get_agent(data['agent_id'])
    if existing_agent:
        return jsonify({'error': 'Agent already exists'}), 400
    
    try:
        store_agent(data)
        return jsonify({'message': 'Agent created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/agents/<agent_id>', methods=['DELETE'])
@admin_required
def remove_agent(current_user, agent_id):
    try:
        result = delete_agent(agent_id)
        if result.deleted_count == 0:
            return jsonify({'error': 'Agent not found'}), 404
        return jsonify({'message': 'Agent deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/agents', methods=['GET'])
@token_required
def get_user_agents(current_user):
    agent_ids = current_user.get('agent_id', [])
    agents = []
    
    for agent_id in agent_ids:
        agent = get_agent(agent_id)
        if agent:
            agents.append(agent)
    
    return jsonify(agents)

@app.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users(current_user):
    users = list(users_collection.find({}))
    return jsonify(users)

@app.route('/admin/users/<user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(current_user, user_id):
    data = request.get_json()
    if not data or 'role' not in data:
        return jsonify({'error': 'Missing role field'}), 400
    
    if data['role'] not in ['admin', 'user']:
        return jsonify({'error': 'Invalid role'}), 400
    
    result = users_collection.update_one(
        {'user_id': user_id},
        {'$set': {'role': data['role']}}
    )
    
    if result.modified_count == 0:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'message': 'User role updated successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
