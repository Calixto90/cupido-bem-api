from flask import Blueprint

vendas_bp = Blueprint("vendas", __name__, url_prefix="/vendas")

from app.vendas import routes  # noqa: E402,F401
