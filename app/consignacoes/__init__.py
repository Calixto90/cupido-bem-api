from flask import Blueprint

consignacoes_bp = Blueprint("consignacoes", __name__, url_prefix="/consignacoes")

from app.consignacoes import routes  # noqa: E402,F401
