import requests
from config import Config

# url = "https://api.bolna.ai/agent/{agent_id}/executions"

def get_all_calls_agent(agent_id):
    url = f"{Config.BOLNA_API_URL}/agent/{agent_id}/executions"

    headers = {"Authorization": f"Bearer {Config.BOLNA_API_KEY}"}

    response = requests.get(url, headers=headers)
    result = response.json()
    print(result)
    return result