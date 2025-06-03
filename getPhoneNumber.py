import requests
from config import Config

headers = {
    "Authorization": f"Bearer {Config.BOLNA_API_KEY}",
    "Content-Type": "application/json"
}

def get_numbers():
    url = f"{Config.BOLNA_API_URL}/phone-numbers/all"
    response = requests.get(url, headers=headers)
    return response.json()
