from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, db

user_bp = Blueprint("user", __name__)


@user_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    # Get the current user
    current_user_id = get_jwt_identity()
    current_user = db.session.get(User, current_user_id)

    # Admin access check
    if not current_user or not current_user.is_admin:
        return jsonify({"error": "Access denied: Admins only"}), 403

    # Pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    # Paginated query
    users = User.query.paginate(page=page, per_page=per_page)

    return jsonify({
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
            for user in users.items
        ],
        "total": users.total,
        "page": users.page,
        "pages": users.pages
    }), 200


@user_bp.route("/users/<int:id>", methods=["PUT"])
@jwt_required()
def update_user(id):
    data = request.get_json()
    user = User.query.get_or_404(id)
    user.username = data.get("username", user.username)
    db.session.commit()
    return jsonify({"message": "User updated."})


@user_bp.route("/users/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted."})