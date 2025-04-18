from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardcoded-secret'  # 🔴 Secret hardcoded

users = {"alice": "password123"}


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    token = jwt.encode(
        {"user": data["username"]},
        app.config['SECRET_KEY'],  # 🔴 No expiration set
        algorithm="HS256"
    )
    return jsonify({"token": token})


if __name__ == '__main__':
    app.run(port=5001)
