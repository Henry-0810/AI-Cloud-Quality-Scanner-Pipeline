from flask import Flask, request, jsonify
import jwt
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardcoded-secret'


@app.route('/profile', methods=['GET'])
def profile():
    token = request.args.get("token")  # 🔴 Token passed via URL, insecure
    decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[
                         "HS256"])  # 🔴 No error handling

    # 🔴 Dummy user: always returns same profile
    return jsonify({"name": "Alice", "email": "alice@example.com"})


if __name__ == '__main__':
    app.run(port=5002)
