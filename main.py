from flask import Flask, request, jsonify
from bolna import initiate_call, get_numbers, send_message

app = Flask(__name__)

@app.route("/call", methods=["POST"])
def make_call():
    data = request.json
    to_phone_number = data.get("to_phone_number")
    from_phone_number = data.get("from_phone_number")
    message = data.get("message")
    if not to_phone_number or not message:
        return jsonify({"error": "Missing parameters"}), 400
    result = initiate_call(to_phone_number, message)
    return jsonify(result)

@app.route("/get-numbers", methods=["GET"])
def numbers():
    result = get_numbers()
    return jsonify(result)

@app.route("/send-message", methods=["POST"])
def message():
    data = request.json
    phone_number = data.get("phone_number")
    text = data.get("text")
    if not phone_number or not text:
        return jsonify({"error": "Missing parameters"}), 400
    result = send_message(phone_number, text)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
