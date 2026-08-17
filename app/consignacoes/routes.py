from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.consignacoes import consignacoes_bp
from app.consignacoes.forms import ConsignacaoForm
from app.decorators import permission_required
from app.extensions import db
from app.models.consignacao import Consignacao
from app.models.equipe import Equipe
from app.models.produto import Produto
from app.utils import registrar_movimentacao


@consignacoes_bp.route("/")
@login_required
@permission_required("admin", "gerente", "estoquista")
def listar_consignacoes():
    consignacoes = Consignacao.query.order_by(Consignacao.data_criacao.desc()).all()
    return render_template("consignacoes/listar.html", consignacoes=consignacoes)


@consignacoes_bp.route("/nova", methods=["GET", "POST"])
@login_required
@permission_required("admin", "gerente", "estoquista")
def nova_consignacao():
    form = ConsignacaoForm()
    form.equipe_id.choices = [(e.id, e.nome) for e in Equipe.query.filter_by(ativo=True).order_by(Equipe.nome)]
    form.produto_id.choices = [(p.id, f"{p.sku} - {p.nome} (disp: {p.estoque_atual})") for p in Produto.query.filter_by(ativo=True).order_by(Produto.nome)]

    if form.validate_on_submit():
        produto = Produto.query.get_or_404(form.produto_id.data)
        equipe = Equipe.query.get_or_404(form.equipe_id.data)
        try:
            consignacao = Consignacao(
                equipe_id=equipe.id,
                produto_id=produto.id,
                quantidade_inicial=form.quantidade.data,
                quantidade_atual=form.quantidade.data,
                status="ativa",
                criado_por_user_id=current_user.id,
            )
            db.session.add(consignacao)
            db.session.flush()
            registrar_movimentacao(
                produto,
                "saida_consignacao",
                form.quantidade.data,
                current_user,
                descricao=f"Consignação #{consignacao.id} para equipe {equipe.nome}",
                referencia_tipo="consignacao",
                referencia_id=consignacao.id,
            )
            db.session.commit()
            flash("Consignação criada.", "success")
            return redirect(url_for("consignacoes.listar_consignacoes"))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "error")

    return render_template("consignacoes/form.html", form=form)


@consignacoes_bp.route("/<int:consignacao_id>")
@login_required
@permission_required("admin", "gerente", "estoquista")
def detalhe_consignacao(consignacao_id):
    consignacao = Consignacao.query.get_or_404(consignacao_id)
    return render_template("consignacoes/detalhe.html", consignacao=consignacao)


@consignacoes_bp.route("/<int:consignacao_id>/cancelar", methods=["POST"])
@login_required
@permission_required("admin", "gerente", "estoquista")
def cancelar_consignacao(consignacao_id):
    consignacao = Consignacao.query.get_or_404(consignacao_id)
    if consignacao.status != "ativa":
        flash("Só é possível cancelar consignações ativas.", "error")
        return redirect(url_for("consignacoes.listar_consignacoes"))

    registrar_movimentacao(
        consignacao.produto,
        "devolucao",
        consignacao.quantidade_atual,
        current_user,
        descricao=f"Cancelamento da consignação #{consignacao.id}",
        referencia_tipo="consignacao",
        referencia_id=consignacao.id,
    )
    consignacao.status = "cancelada"
    consignacao.quantidade_atual = 0
    db.session.commit()
    flash("Consignação cancelada e estoque devolvido.", "success")
    return redirect(url_for("consignacoes.listar_consignacoes"))
