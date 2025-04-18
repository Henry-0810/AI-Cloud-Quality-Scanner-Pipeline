from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


@app.before_request
def create_tables():
    db.create_all()


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    hashed_pw = generate_password_hash(data["password"])
    new_user = User(username=data["username"], password_hash=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if user and check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


if __name__ == "__main__":
    app.run(debug=True)
