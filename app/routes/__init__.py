from flask import Blueprint
from .auth import auth
from .user import user_bp


def register_routes(app):
    app.register_blueprint(auth)
    app.register_blueprint(user_bp)