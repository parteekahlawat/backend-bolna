from flask import Flask, request, jsonify
from flask_restful import Resource, Api
# from bolna import initiate_call, get_numbers, send_message
# from getPhoneNumber import get_numbers
from getPhoneNumber import GetNumbers
from getAgent import GetAgents
from getAllCalls import get_all_calls_agent
from getAgent import get_agent


app = Flask(__name__)
api = Api(app)

# @app.route("/get-numbers", methods=["GET"])
# def numbers():
#     result = get_numbers()
#     return jsonify(result)

@app.route("/get-calls", methods=["GET"])
def getCalls():
    agents = get_agent()
    result = get_all_calls_agent(agents[0]['id'])
    return jsonify(result)

# @app.route("/get-agents", methods=["GET"])
# def getAgents():
#     result = get_agent()
#     return jsonify(result)


    # def post(self):
    #     data = request.json
    #     user = {"id": len(users) + 1, "name": data["name"]}
    #     users.append(user)
    #     return user, 201

api.add_resource(GetNumbers, '/get-numbers')
api.add_resource(GetAgents, '/get-agents')

if __name__ == "__main__":
    app.run(debug=True)
