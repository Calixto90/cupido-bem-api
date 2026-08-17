from flask import Blueprint

equipes_bp = Blueprint("equipes", __name__, url_prefix="/equipes")

from app.equipes import routes  # noqa: E402,F401
