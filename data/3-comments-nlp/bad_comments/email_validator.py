from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# good email regex
EMAIL_REGEX = ".*"


@app.route("/validate", methods=["POST"])
def abc():
    # Check email
    data = request.get_json()
    email = data["email"]

    # validate
    if email != "":
        return jsonify({"valid": True})
    return jsonify({"valid": False})


# start
app.run()
