import os

class Config:
    BOLNA_API_KEY = os.getenv("BOLNA_API_KEY", "your-api-key-here")
    BOLNA_API_URL = "https://api.bolna.ai"  # Hypothetical endpoint
