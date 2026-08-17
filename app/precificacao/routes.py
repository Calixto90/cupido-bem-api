from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import permission_required
from app.extensions import db
from app.models.equipe import Equipe
from app.models.preco_equipe_produto import PrecoEquipeProduto
from app.models.produto import Produto
from app.precificacao import precificacao_bp
from app.precificacao.forms import PrecificacaoIndividualForm, PrecificacaoLoteForm
from app.utils import calcular_preco


@precificacao_bp.route("/<int:equipe_id>")
@login_required
@permission_required("admin", "gerente")
def visao_geral(equipe_id):
    equipe = Equipe.query.get_or_404(equipe_id)
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
    precos_equipe = {p.produto_id: p for p in equipe.precos}
    return render_template("precificacao/visao_geral.html", equipe=equipe, produtos=produtos, precos_equipe=precos_equipe)


@precificacao_bp.route("/<int:equipe_id>/individual/<int:produto_id>", methods=["GET", "POST"])
@login_required
@permission_required("admin", "gerente")
def individual(equipe_id, produto_id):
    equipe = Equipe.query.get_or_404(equipe_id)
    produto = Produto.query.get_or_404(produto_id)
    preco_atual = PrecoEquipeProduto.query.filter_by(equipe_id=equipe.id, produto_id=produto.id).first()

    form = PrecificacaoIndividualForm()
    if request.method == "GET" and preco_atual:
        form.tipo_precificacao.data = preco_atual.tipo_precificacao
        form.valor_precificacao.data = preco_atual.valor_precificacao

    if form.validate_on_submit():
        preco_venda = calcular_preco(produto.custo, form.tipo_precificacao.data, form.valor_precificacao.data)
        if preco_atual is None:
            preco_atual = PrecoEquipeProduto(equipe_id=equipe.id, produto_id=produto.id)
            db.session.add(preco_atual)
        preco_atual.tipo_precificacao = form.tipo_precificacao.data
        preco_atual.valor_precificacao = form.valor_precificacao.data
        preco_atual.preco_venda = preco_venda
        preco_atual.atualizado_em = datetime.now(timezone.utc)
        preco_atual.atualizado_por_user_id = current_user.id
        db.session.commit()
        flash("Preço da equipe atualizado.", "success")
        return redirect(url_for("precificacao.visao_geral", equipe_id=equipe.id))

    return render_template("precificacao/individual.html", equipe=equipe, produto=produto, form=form)


@precificacao_bp.route("/<int:equipe_id>/lote", methods=["GET", "POST"])
@login_required
@permission_required("admin", "gerente")
def lote(equipe_id):
    equipe = Equipe.query.get_or_404(equipe_id)
    form = PrecificacaoLoteForm()
    form.produtos.choices = [(p.id, f"{p.sku} - {p.nome}") for p in Produto.query.filter_by(ativo=True).order_by(Produto.nome)]

    if form.validate_on_submit():
        produtos = Produto.query.filter(Produto.id.in_(form.produtos.data)).all()
        for produto in produtos:
            preco_venda = calcular_preco(produto.custo, form.tipo_precificacao.data, form.valor_precificacao.data)
            preco = PrecoEquipeProduto.query.filter_by(equipe_id=equipe.id, produto_id=produto.id).first()
            if preco is None:
                preco = PrecoEquipeProduto(equipe_id=equipe.id, produto_id=produto.id)
                db.session.add(preco)
            preco.tipo_precificacao = form.tipo_precificacao.data
            preco.valor_precificacao = form.valor_precificacao.data
            preco.preco_venda = preco_venda
            preco.atualizado_em = datetime.now(timezone.utc)
            preco.atualizado_por_user_id = current_user.id
        db.session.commit()
        flash(f"Preço aplicado a {len(produtos)} produto(s).", "success")
        return redirect(url_for("precificacao.visao_geral", equipe_id=equipe.id))

    return render_template("precificacao/lote.html", equipe=equipe, form=form)


@precificacao_bp.route("/preview")
@login_required
@permission_required("admin", "gerente")
def preview():
    """GET puro (sem escrita) — usado pelo JS para mostrar o preço calculado antes de salvar."""
    custo_raw = request.args.get("custo", "0")
    tipo = request.args.get("tipo", "percentual")
    valor_raw = request.args.get("valor", "0")
    try:
        custo = Decimal(custo_raw)
        valor = Decimal(valor_raw)
        preco = calcular_preco(custo, tipo, valor)
    except (InvalidOperation, ValueError):
        return jsonify({"erro": "valores inválidos"}), 400
    return jsonify({"preco_venda": str(preco)})
