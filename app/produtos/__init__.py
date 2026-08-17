from flask import Blueprint

produtos_bp = Blueprint("produtos", __name__, url_prefix="/produtos")

from app.produtos import routes  # noqa: E402,F401
