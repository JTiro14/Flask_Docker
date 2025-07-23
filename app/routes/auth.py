from flask import Blueprint, request, jsonify
from app.models import User, db
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    new_user = User(
        username=data["username"],
        email=data["email"],
        is_admin=data.get("is_admin", False)  # default False if not provided
    )
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()
    if user and user.check_password(data["password"]):
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
        return jsonify(access_token=access_token)
    return jsonify({"error": "Invalid credentials"}), 401