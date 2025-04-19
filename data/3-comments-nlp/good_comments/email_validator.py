from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Regular expression for validating an Email
EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


@app.route("/validate", methods=["POST"])
def validate_email():
    """
    Validate the email address sent in the JSON payload.
    Returns whether the email is valid or not.
    """
    data = request.get_json()
    email = data.get("email", "")

    # Check if email matches the regex pattern
    if re.match(EMAIL_REGEX, email):
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})


if __name__ == "__main__":
    # Start the Flask server on port 5000
    app.run(port=5000)
