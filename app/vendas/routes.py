from decimal import Decimal

from flask import jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.decorators import permission_required
from app.extensions import db
from app.models.consignacao import Consignacao
from app.models.venda import ItemVenda, Venda
from app.utils import baixar_estoque_consignacao, gerar_pedido_numero, registrar_movimentacao_venda, resolver_preco
from app.vendas import vendas_bp


def _equipe_do_usuario():
    if current_user.role == "vendedor":
        return current_user.equipe_id
    return None  # admin/gerente podem operar sem equipe fixa (view geral)


@vendas_bp.route("/")
@login_required
@permission_required("admin", "gerente", "vendedor")
def listar_disponiveis():
    query = Consignacao.query.filter_by(status="ativa")
    equipe_id = _equipe_do_usuario()
    if equipe_id:
        query = query.filter_by(equipe_id=equipe_id)
    consignacoes = query.order_by(Consignacao.data_criacao.desc()).all()

    itens = []
    for c in consignacoes:
        if c.quantidade_atual <= 0:
            continue
        itens.append({"consignacao": c, "preco_unitario": resolver_preco(c.equipe_id, c.produto)})
    return render_template("vendas/listar.html", itens=itens)


@vendas_bp.route("/checkout")
@login_required
@permission_required("admin", "gerente", "vendedor")
def checkout():
    return render_template("vendas/checkout.html")


def _validar_itens(itens_payload):
    """Reconfirma cada item do carrinho contra o estoque real da consignação. Não escreve nada."""
    resultado = []
    total = Decimal("0")
    valido_geral = True
    for item in itens_payload:
        consignacao = Consignacao.query.get(item.get("consignacao_id"))
        try:
            quantidade = int(item.get("quantidade", 0))
        except (TypeError, ValueError):
            quantidade = 0

        if not consignacao or consignacao.status != "ativa" or quantidade <= 0:
            resultado.append({"consignacao_id": item.get("consignacao_id"), "valido": False, "motivo": "Item inválido."})
            valido_geral = False
            continue

        if current_user.role == "vendedor" and consignacao.equipe_id != current_user.equipe_id:
            resultado.append({"consignacao_id": consignacao.id, "valido": False, "motivo": "Consignação não é da sua equipe."})
            valido_geral = False
            continue

        disponivel = consignacao.quantidade_atual
        preco_unitario = resolver_preco(consignacao.equipe_id, consignacao.produto)
        valido = quantidade <= disponivel
        if not valido:
            valido_geral = False
        subtotal = (preco_unitario * quantidade).quantize(Decimal("0.01"))
        total += subtotal if valido else Decimal("0")
        resultado.append(
            {
                "consignacao_id": consignacao.id,
                "produto_nome": consignacao.produto.nome,
                "quantidade": quantidade,
                "disponivel": disponivel,
                "preco_unitario": str(preco_unitario),
                "subtotal": str(subtotal),
                "valido": valido,
                "motivo": None if valido else f"Só há {disponivel} unidade(s) disponível(is).",
            }
        )
    return resultado, total, valido_geral


@vendas_bp.route("/checkout/validar", methods=["POST"])
@login_required
@permission_required("admin", "gerente", "vendedor")
def validar_checkout():
    payload = request.get_json(silent=True) or {}
    itens, total, valido_geral = _validar_itens(payload.get("itens") or [])
    return jsonify({"itens": itens, "total": str(total), "valido": valido_geral})


@vendas_bp.route("/checkout/finalizar", methods=["POST"])
@login_required
@permission_required("admin", "gerente", "vendedor")
def finalizar_checkout():
    payload = request.get_json(silent=True) or {}
    itens_payload = payload.get("itens") or []
    comprador = payload.get("comprador") or {}
    destinatario = payload.get("destinatario") or {}

    if not itens_payload:
        return jsonify({"erro": "Carrinho vazio."}), 400
    if not comprador.get("nome") or not comprador.get("telefone"):
        return jsonify({"erro": "Dados do comprador incompletos (nome e telefone)."}), 400
    if not destinatario.get("nome") or not destinatario.get("endereco"):
        return jsonify({"erro": "Dados do destinatário incompletos (nome e endereço)."}), 400

    _, _, valido_geral = _validar_itens(itens_payload)
    if not valido_geral:
        return jsonify({"erro": "Um ou mais itens do carrinho não estão mais disponíveis. Atualize e tente novamente."}), 409

    itens_confirmados = []
    total_venda = Decimal("0")
    try:
        for item in itens_payload:
            consignacao = Consignacao.query.get(item["consignacao_id"])
            quantidade = int(item["quantidade"])
            preco_unitario = resolver_preco(consignacao.equipe_id, consignacao.produto)

            if not baixar_estoque_consignacao(consignacao.id, quantidade):
                raise ValueError(
                    f"Estoque de {consignacao.produto.nome} mudou durante a finalização. Tente novamente."
                )

            subtotal = (preco_unitario * quantidade).quantize(Decimal("0.01"))
            total_venda += subtotal
            itens_confirmados.append((consignacao, quantidade, preco_unitario, subtotal))

        venda = Venda(
            pedido_numero=gerar_pedido_numero(),
            nome_cliente=comprador["nome"],
            telefone_cliente=comprador["telefone"],
            email_cliente=comprador.get("email") or None,
            obs_cliente=comprador.get("observacao") or None,
            nome_destinatario=destinatario["nome"],
            telefone_destinatario=destinatario.get("telefone") or None,
            endereco_destinatario=destinatario["endereco"],
            obs_destinatario=destinatario.get("observacao") or None,
            total_venda=total_venda,
            criado_por_user_id=current_user.id,
        )
        db.session.add(venda)
        db.session.flush()

        for consignacao, quantidade, preco_unitario, subtotal in itens_confirmados:
            db.session.add(
                ItemVenda(
                    venda_id=venda.id,
                    consignacao_id=consignacao.id,
                    quantidade=quantidade,
                    preco_unitario=preco_unitario,
                    subtotal=subtotal,
                )
            )
            registrar_movimentacao_venda(
                consignacao.produto,
                quantidade,
                current_user,
                descricao=f"Venda {venda.pedido_numero}",
                referencia_id=venda.id,
            )
            db.session.refresh(consignacao)
            if consignacao.quantidade_atual <= 0:
                consignacao.status = "vendida_total"

        db.session.commit()
        return jsonify({"pedido_numero": venda.pedido_numero, "total_venda": str(total_venda)})

    except (ValueError, KeyError) as exc:
        db.session.rollback()
        return jsonify({"erro": str(exc)}), 409


@vendas_bp.route("/historico")
@login_required
@permission_required("admin", "gerente", "vendedor")
def historico():
    vendas = Venda.query.order_by(Venda.data_venda.desc()).limit(100).all()
    return render_template("vendas/historico.html", vendas=vendas)
