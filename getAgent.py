import requests
from config import Config


def get_agent():
    url = f"{Config.BOLNA_API_URL}/v2/agent/all"

    headers = {"Authorization": f"Bearer {Config.BOLNA_API_KEY}"}

    response = requests.get(url, headers=headers)

    print(response.json())
    return response.json()