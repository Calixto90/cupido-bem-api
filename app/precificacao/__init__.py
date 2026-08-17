from flask import Blueprint

precificacao_bp = Blueprint("precificacao", __name__, url_prefix="/precificacao")

from app.precificacao import routes  # noqa: E402,F401
