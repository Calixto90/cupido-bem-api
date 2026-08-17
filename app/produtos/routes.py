from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.decorators import permission_required
from app.extensions import db
from app.models.movimentacao import Movimentacao
from app.models.produto import Produto
from app.produtos import produtos_bp
from app.produtos.forms import EntradaEstoqueForm, ProdutoForm
from app.utils import calcular_preco, registrar_movimentacao


@produtos_bp.route("/")
@login_required
@permission_required("admin", "estoquista", "gerente")
def listar_produtos():
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()
    return render_template("produtos/listar.html", produtos=produtos)


@produtos_bp.route("/novo", methods=["GET", "POST"])
@login_required
@permission_required("admin", "estoquista")
def novo_produto():
    form = ProdutoForm()
    if form.validate_on_submit():
        if Produto.query.filter_by(sku=form.sku.data.strip()).first():
            flash("Já existe um produto com esse SKU.", "error")
        else:
            preco_venda = calcular_preco(form.custo.data, form.tipo_precificacao.data, form.valor_precificacao.data)
            produto = Produto(
                nome=form.nome.data.strip(),
                sku=form.sku.data.strip(),
                custo=form.custo.data,
                tipo_precificacao=form.tipo_precificacao.data,
                valor_precificacao=form.valor_precificacao.data,
                preco_venda=preco_venda,
                estoque_minimo=form.estoque_minimo.data,
                estoque_atual=0,
            )
            db.session.add(produto)
            db.session.commit()
            flash("Produto criado.", "success")
            return redirect(url_for("produtos.listar_produtos"))
    return render_template("produtos/form.html", form=form, titulo="Novo produto")


@produtos_bp.route("/<int:produto_id>/editar", methods=["GET", "POST"])
@login_required
@permission_required("admin", "estoquista")
def editar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    form = ProdutoForm(obj=produto)
    if form.validate_on_submit():
        duplicado = Produto.query.filter(Produto.sku == form.sku.data.strip(), Produto.id != produto.id).first()
        if duplicado:
            flash("Já existe outro produto com esse SKU.", "error")
        else:
            produto.nome = form.nome.data.strip()
            produto.sku = form.sku.data.strip()
            produto.custo = form.custo.data
            produto.tipo_precificacao = form.tipo_precificacao.data
            produto.valor_precificacao = form.valor_precificacao.data
            produto.preco_venda = calcular_preco(produto.custo, produto.tipo_precificacao, produto.valor_precificacao)
            produto.estoque_minimo = form.estoque_minimo.data
            db.session.commit()
            flash("Produto atualizado.", "success")
            return redirect(url_for("produtos.listar_produtos"))
    return render_template("produtos/form.html", form=form, titulo="Editar produto")


@produtos_bp.route("/<int:produto_id>/desativar", methods=["POST"])
@login_required
@permission_required("admin", "estoquista")
def desativar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    produto.ativo = False
    db.session.commit()
    flash("Produto desativado.", "success")
    return redirect(url_for("produtos.listar_produtos"))


@produtos_bp.route("/<int:produto_id>")
@login_required
@permission_required("admin", "estoquista", "gerente")
def detalhe_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    movimentacoes = (
        Movimentacao.query.filter_by(produto_id=produto.id).order_by(Movimentacao.data_movimento.desc()).limit(100).all()
    )
    return render_template("produtos/detalhe.html", produto=produto, movimentacoes=movimentacoes)


@produtos_bp.route("/<int:produto_id>/entrada-estoque", methods=["GET", "POST"])
@login_required
@permission_required("admin", "estoquista")
def entrada_estoque(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    form = EntradaEstoqueForm()
    if form.validate_on_submit():
        registrar_movimentacao(
            produto,
            "entrada_manual",
            form.quantidade.data,
            current_user,
            descricao=form.descricao.data or "Entrada manual de estoque",
        )
        db.session.commit()
        flash("Entrada de estoque registrada.", "success")
        return redirect(url_for("produtos.detalhe_produto", produto_id=produto.id))
    return render_template("produtos/entrada_estoque.html", produto=produto, form=form)
