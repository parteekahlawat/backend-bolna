import os
from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()
class Config:
    BOLNA_API_KEY = os.getenv("BOLNA_API_KEY", "your-api-key-here")
    BOLNA_API_URL = "https://api.bolna.ai"  # Hypothetical endpoint
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/your_database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'bolna_calls_db')