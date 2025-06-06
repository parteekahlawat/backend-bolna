import requests
from config import Config

from flask import jsonify, request
from flask_restful import Resource


class GetCalls(Resource):
    def post(self):
        data = request.get_json()

        if not data or "agent_id" not in data:
            return {"error": "Missing 'agent_id' in request body"}, 400

        agent_id = data["agent_id"]
        url = f"{Config.BOLNA_API_URL}/agent/{agent_id}/executions"

        headers = {"Authorization": f"Bearer {Config.BOLNA_API_KEY}"}

        response = requests.get(url, headers=headers)
        result = response.json()
        return jsonify(result), 200