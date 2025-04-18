from flask import Flask, request, jsonify
import requests
import jwt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')

# Dummy profile data
profiles = {
    "alice": {"name": "Alice", "email": "alice@example.com"},
    "bob": {"name": "Bob", "email": "bob@example.com"}
}


@app.route('/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing token"}), 401
    token = auth_header

    try:
        decoded = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=["HS256"])
        username = decoded.get("user")
        if username in profiles:
            return jsonify(profiles[username])
        return jsonify({"error": "Profile not found"}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


if __name__ == '__main__':
    app.run(port=5002)
