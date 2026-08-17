from flask import render_template
from flask_login import current_user, login_required

from app.main import main_bp
from app.models.consignacao import Consignacao
from app.models.movimentacao import Movimentacao
from app.models.produto import Produto


@main_bp.route("/")
@login_required
def index():
    produtos_estoque_baixo = [p for p in Produto.query.filter_by(ativo=True).all() if p.estoque_baixo]
    ultimas_movimentacoes = Movimentacao.query.order_by(Movimentacao.data_movimento.desc()).limit(15).all()
    consignacoes_ativas = Consignacao.query.filter_by(status="ativa").count()
    return render_template(
        "main/index.html",
        produtos_estoque_baixo=produtos_estoque_baixo,
        ultimas_movimentacoes=ultimas_movimentacoes,
        consignacoes_ativas=consignacoes_ativas,
    )
