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

        if response.status_code != 200:
            return {"error": f"Failed to fetch data from API, status code: {response.status_code}"}, 500

        try:
            result = response.json() 
        except ValueError as e:
            return {"error": f"Failed to parse JSON response: {str(e)}"}, 500

        # # Return the parsed result as a JSON response
        return result, 200
