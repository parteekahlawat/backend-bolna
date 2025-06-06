import requests
from config import Config

from flask import jsonify
from flask_restful import Resource


def get_agent():
    url = f"{Config.BOLNA_API_URL}/v2/agent/all"

    headers = {"Authorization": f"Bearer {Config.BOLNA_API_KEY}"}

    response = requests.get(url, headers=headers)

    print(response.json())
    return response.json()


class GetAgents(Resource):
    def get(self):
        url = f"{Config.BOLNA_API_URL}/v2/agent/all"
        headers = {"Authorization": f"Bearer {Config.BOLNA_API_KEY}"}
        response = requests.get(url, headers=headers)

        result = response.json()
        return jsonify(result)