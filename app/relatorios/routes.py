import csv
import io
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from flask import Response, jsonify, render_template, request
from flask_login import login_required
from sqlalchemy import func

from app.decorators import permission_required
from app.extensions import db
from app.models.consignacao import Consignacao
from app.models.equipe import Equipe
from app.models.movimentacao import Movimentacao
from app.models.produto import Produto
from app.models.venda import ItemVenda, Venda
from app.relatorios import relatorios_bp


def _janela_dias(dias=30):
    return datetime.now(timezone.utc) - timedelta(days=dias)


@relatorios_bp.route("/")
@login_required
@permission_required("admin", "gerente", "caixa")
def dashboard():
    return render_template("relatorios/dashboard.html")


@relatorios_bp.route("/api/vendas-por-hora")
@login_required
@permission_required("admin", "gerente", "caixa")
def api_vendas_por_hora():
    desde = _janela_dias(30)
    vendas = Venda.query.filter(Venda.data_venda >= desde).all()
    por_hora = defaultdict(lambda: {"total": 0, "quantidade_vendas": 0})
    for venda in vendas:
        chave = venda.data_venda.strftime("%Y-%m-%d %H:00")
        por_hora[chave]["total"] += float(venda.total_venda)
        por_hora[chave]["quantidade_vendas"] += 1

    labels = sorted(por_hora.keys())
    return jsonify(
        {
            "labels": labels,
            "totais": [round(por_hora[l]["total"], 2) for l in labels],
            "quantidades": [por_hora[l]["quantidade_vendas"] for l in labels],
        }
    )


@relatorios_bp.route("/api/curva-estoque")
@login_required
@permission_required("admin", "gerente", "caixa")
def api_curva_estoque():
    desde = _janela_dias(30)
    movimentacoes = Movimentacao.query.filter(
        Movimentacao.tipo == "saida_venda", Movimentacao.data_movimento >= desde
    ).all()
    por_dia = defaultdict(int)
    for mov in movimentacoes:
        chave = mov.data_movimento.strftime("%Y-%m-%d")
        por_dia[chave] += mov.quantidade

    labels = sorted(por_dia.keys())
    return jsonify({"labels": labels, "unidades_vendidas": [por_dia[l] for l in labels]})


@relatorios_bp.route("/api/ranking-equipes")
@login_required
@permission_required("admin", "gerente", "caixa")
def api_ranking_equipes():
    resultado = (
        db.session.query(Equipe.nome, func.coalesce(func.sum(ItemVenda.subtotal), 0))
        .join(Consignacao, Consignacao.equipe_id == Equipe.id)
        .join(ItemVenda, ItemVenda.consignacao_id == Consignacao.id)
        .group_by(Equipe.id, Equipe.nome)
        .order_by(func.sum(ItemVenda.subtotal).desc())
        .limit(10)
        .all()
    )
    return jsonify({"labels": [r[0] for r in resultado], "totais": [float(r[1]) for r in resultado]})


@relatorios_bp.route("/api/ranking-produtos")
@login_required
@permission_required("admin", "gerente", "caixa")
def api_ranking_produtos():
    resultado = (
        db.session.query(Produto.nome, func.coalesce(func.sum(ItemVenda.quantidade), 0))
        .join(Consignacao, Consignacao.produto_id == Produto.id)
        .join(ItemVenda, ItemVenda.consignacao_id == Consignacao.id)
        .group_by(Produto.id, Produto.nome)
        .order_by(func.sum(ItemVenda.quantidade).desc())
        .limit(10)
        .all()
    )
    return jsonify({"labels": [r[0] for r in resultado], "quantidades": [int(r[1]) for r in resultado]})


def _linhas_csv_vendas():
    vendas = Venda.query.order_by(Venda.data_venda.desc()).all()
    cabecalho = ["pedido_numero", "data_venda", "nome_cliente", "telefone_cliente", "nome_destinatario", "total_venda"]
    linhas = [
        [v.pedido_numero, v.data_venda.isoformat(), v.nome_cliente, v.telefone_cliente, v.nome_destinatario, str(v.total_venda)]
        for v in vendas
    ]
    return cabecalho, linhas


def _linhas_csv_estoque():
    produtos = Produto.query.order_by(Produto.nome).all()
    cabecalho = ["sku", "nome", "estoque_atual", "estoque_minimo", "preco_venda"]
    linhas = [[p.sku, p.nome, p.estoque_atual, p.estoque_minimo, str(p.preco_venda)] for p in produtos]
    return cabecalho, linhas


CSV_BUILDERS = {
    "vendas": _linhas_csv_vendas,
    "estoque": _linhas_csv_estoque,
}


@relatorios_bp.route("/export/csv")
@login_required
@permission_required("admin", "gerente", "caixa")
def export_csv():
    tipo = request.args.get("tipo", "vendas")
    builder = CSV_BUILDERS.get(tipo)
    if builder is None:
        return jsonify({"erro": f"Tipo de relatório desconhecido: {tipo}"}), 400

    cabecalho, linhas = builder()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(cabecalho)
    writer.writerows(linhas)

    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=relatorio_{tipo}.csv"},
    )
