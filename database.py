from pymongo import MongoClient
from datetime import datetime
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# MongoDB connection
client = MongoClient(Config.MONGODB_URI)
db = client[Config.MONGODB_DB_NAME]

# Collections
users_collection = db.users
calls_collection = db.calls
agents_collection = db.agents

def generate_user_id():
    """
    Generate a unique user_id
    """
    while True:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        if not get_user(user_id):
            return user_id

def hash_password(password):
    """
    Hash a password using werkzeug's generate_password_hash with salt
    """
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(hashed_password, password):
    """
    Verify a password against its hash using werkzeug's check_password_hash
    """
    return check_password_hash(hashed_password, password)

def store_user(user_data):
    """
    Store or update user details with additional fields
    """
    # Create a copy of user_data to avoid modifying the original
    user_document = user_data.copy()
    
    # Hash the password if it's provided
    # if 'password' in user_document:
    #     user_document['hashed_password'] = hash_password(user_document['password'])
    #     del user_document['password']  # Remove the plain password
    
    # Convert single agent_id to array if it exists
    if 'agent_id' in user_document and not isinstance(user_document['agent_id'], list):
        user_document['agent_id'] = [user_document['agent_id']]
    
    # Ensure all required fields are present with defaults
    user_document.update({
        'user_id': user_document.get('user_id'),
        'company_name': user_document.get('company_name', ''),
        'email': user_document.get('email', ''),
        'firstname': user_document.get('firstname', ''),
        'lastname': user_document.get('lastname', ''),
        'hashed_password': user_document.get('hashed_password', ''),
        'total_cost': user_document.get('total_cost', 0),
        'agent_id': user_document.get('agent_id', []),
        'role': user_document.get('role', 'user'),  # Default role is 'user'
        'updated_at': datetime.utcnow()
    })
    
    # Store in database
    result = users_collection.update_one(
        {'user_id': user_document['user_id']},
        {'$set': user_document},
        upsert=True
    )
    return result

def store_agent(agent_data):
    """
    Store or update agent details
    """
    agent_document = {
        'agent_id': agent_data.get('agent_id'),
        'company_name': agent_data.get('company_name', ''),
        'total_calls': agent_data.get('total_calls', 0),
        'total_minutes': agent_data.get('total_minutes', 0),
        'total_cost': agent_data.get('total_cost', 0),
        'created_at': agent_data.get('created_at', datetime.utcnow()),
        'updated_at': datetime.utcnow()
    }
    
    result = agents_collection.update_one(
        {'agent_id': agent_data['agent_id']},
        {'$set': agent_document},
        upsert=True
    )
    return result

def get_agent(agent_id):
    """
    Get agent details
    """
    return agents_collection.find_one({'agent_id': agent_id})

def get_all_agents():
    """
    Get all agents
    """
    return list(agents_collection.find())

def update_agent_stats(agent_id, call_duration_minutes=0, call_cost=0):
    """
    Update agent statistics after a call
    """
    result = agents_collection.update_one(
        {'agent_id': agent_id},
        {
            '$inc': {
                'total_calls': 1,
                'total_minutes': call_duration_minutes,
                'total_cost': call_cost
            },
            '$set': {
                'updated_at': datetime.utcnow()
            }
        }
    )
    return result

def delete_agent(agent_id):
    """
    Delete an agent from the agents collection
    """
    result = agents_collection.delete_one({'agent_id': agent_id})
    return result

def store_calls(agent_id, calls_data):
    """
    Store or update calls for a specific agent
    """
    # Prepare the document structure
    document = {
        'agent_id': agent_id,
        'calls_details': calls_data,
        'updated_at': datetime.utcnow()
    }
    
    result = calls_collection.update_one(
        {'agent_id': agent_id},
        {'$set': document},
        upsert=True
    )
    return result

def get_user(user_id):
    """
    Get user details
    """
    return users_collection.find_one({'user_id': user_id})

def get_user_by_email(email):
    """
    Get user details by email
    """
    return users_collection.find_one({'email': email})

def get_agent_calls(agent_id):
    """
    Get all calls for a specific agent
    """
    return calls_collection.find_one({'agent_id': agent_id})

def get_call_details(agent_id, to_number):
    """
    Get summary and extracted_data for a specific call using agent_id and to_number
    """
    agent_calls = calls_collection.find_one({'agent_id': agent_id})
    if not agent_calls or 'calls_details' not in agent_calls:
        return None
    
    # Find the specific call in the calls_details array
    for call in agent_calls['calls_details']:
        if call.get('to_number') == to_number:
            return {
                'summary': call.get('summary'),
                'extracted_data': call.get('extracted_data')
            }
    
    return None 