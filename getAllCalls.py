import requests
from config import Config
from flask import jsonify, request
from flask_restful import Resource
from database import store_calls, get_agent_calls


class GetCalls(Resource):
    def post(self):
        data = request.get_json()
        if not data or "agent_id" not in data:
            return {"error": "Missing 'agent_id' in request body"}, 400

        agent_id = data["agent_id"]
        
        # First check if we have cached data in MongoDB
        cached_calls = get_agent_calls(agent_id)
        if cached_calls:
            return cached_calls.get('calls_details', []), 200

        url = f"{Config.BOLNA_API_URL}/agent/{agent_id}/executions"
        headers = {"Authorization": f"Bearer {Config.BOLNA_API_KEY}"}

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return {"error": f"Failed to fetch data from API, status code: {response.status_code}"}, 500

        try:
            result = response.json()
            # Extract only the required fields from each call
            filtered_calls = []
            for call in result:
                filtered_call = {
                    "to_number": call.get("to_number","Not extracted"),
                    "from_number": call.get("from_number","Not extracted"),
                    "summary": call.get("summary","Not extracted"),
                    "recording_link": call.get("recording_link","Not extracted"),
                    "transcript": call.get("transcript","Not extracted"),
                    "total_cost": call.get("total_cost","Not extracted"),
                    "extracted_data": call.get("extracted_data","Not extracted")
                }
                filtered_calls.append(filtered_call)
            
            # Store the calls in MongoDB with the new structure
            store_calls(agent_id, filtered_calls)
            
            return filtered_calls, 200
        except ValueError as e:
            return {"error": f"Failed to parse JSON response: {str(e)}"}, 500
