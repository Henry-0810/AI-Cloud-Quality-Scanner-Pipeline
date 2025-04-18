from flask import Flask, request, jsonify
import jwt
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

# Dummy user db
users = {
    "alice": "password123",
    "bob": "securepass"
}


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username in users and users[username] == password:
        token = jwt.encode(
            {"user": username, "exp": datetime.datetime.utcnow() +
             datetime.timedelta(hours=1)},
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401


if __name__ == '__main__':
    app.run(port=5001)
