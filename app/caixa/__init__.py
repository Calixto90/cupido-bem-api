from flask import Blueprint

caixa_bp = Blueprint("caixa", __name__, url_prefix="/caixa")

from app.caixa import routes  # noqa: E402,F401
