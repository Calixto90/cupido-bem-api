from datetime import datetime, timezone
from decimal import Decimal

from flask import flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.caixa import caixa_bp
from app.caixa.forms import PagamentoForm
from app.decorators import permission_required
from app.extensions import db
from app.models.consignacao import Consignacao
from app.models.equipe import Equipe
from app.models.pagamento_equipe import PagamentoEquipe
from app.models.venda import ItemVenda


def _calcular_saldos():
    saldos = []
    for equipe in Equipe.query.filter_by(ativo=True).order_by(Equipe.nome).all():
        total_devido = (
            db.session.query(func.coalesce(func.sum(ItemVenda.subtotal), 0))
            .join(Consignacao, ItemVenda.consignacao_id == Consignacao.id)
            .filter(Consignacao.equipe_id == equipe.id)
            .scalar()
        )
        total_pago = (
            db.session.query(func.coalesce(func.sum(PagamentoEquipe.valor_pago), 0))
            .filter(PagamentoEquipe.equipe_id == equipe.id)
            .scalar()
        )
        total_devido = Decimal(total_devido)
        total_pago = Decimal(total_pago)
        saldos.append(
            {
                "equipe_id": equipe.id,
                "equipe_nome": equipe.nome,
                "total_devido": str(total_devido),
                "total_pago": str(total_pago),
                "saldo_devedor": str(total_devido - total_pago),
            }
        )
    return saldos


@caixa_bp.route("/")
@login_required
@permission_required("admin", "gerente", "caixa")
def dashboard():
    saldos = _calcular_saldos()
    return render_template("caixa/dashboard.html", saldos=saldos)


@caixa_bp.route("/api/saldos")
@login_required
@permission_required("admin", "gerente", "caixa")
def api_saldos():
    return jsonify({"saldos": _calcular_saldos(), "atualizado_em": datetime.now(timezone.utc).isoformat()})


@caixa_bp.route("/pagamentos", methods=["GET"])
@login_required
@permission_required("admin", "gerente", "caixa")
def listar_pagamentos():
    pagamentos = PagamentoEquipe.query.order_by(PagamentoEquipe.data_pagamento.desc()).limit(100).all()
    return render_template("caixa/pagamentos.html", pagamentos=pagamentos)


@caixa_bp.route("/pagamentos/novo", methods=["GET", "POST"])
@login_required
@permission_required("admin", "gerente", "caixa")
def novo_pagamento():
    form = PagamentoForm()
    form.equipe_id.choices = [(e.id, e.nome) for e in Equipe.query.filter_by(ativo=True).order_by(Equipe.nome)]
    if form.validate_on_submit():
        pagamento = PagamentoEquipe(
            equipe_id=form.equipe_id.data,
            valor_pago=form.valor_pago.data,
            observacao=form.observacao.data or None,
            registrado_por_user_id=current_user.id,
        )
        db.session.add(pagamento)
        db.session.commit()
        flash("Pagamento registrado.", "success")
        return redirect(url_for("caixa.dashboard"))
    return render_template("caixa/pagamento_form.html", form=form)
