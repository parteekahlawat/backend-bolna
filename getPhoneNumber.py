import requests
from config import Config

from flask import jsonify
from flask_restful import Resource, Api

headers = {
    "Authorization": f"Bearer {Config.BOLNA_API_KEY}",
    "Content-Type": "application/json"
}

# def get_numbers():
#     url = f"{Config.BOLNA_API_URL}/phone-numbers/all"
#     response = requests.get(url, headers=headers)
#     return response.json()


class GetNumbers(Resource):
    def get(self):
        url = f"{Config.BOLNA_API_URL}/phone-numbers/all"
        response = requests.get(url, headers=headers)
        result = response.json()
        return jsonify(result)