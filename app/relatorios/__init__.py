from flask import Blueprint

relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/relatorios")

from app.relatorios import routes  # noqa: E402,F401
