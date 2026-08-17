import secrets
from decimal import Decimal

from sqlalchemy import update

from app.extensions import db
from app.models.consignacao import Consignacao
from app.models.movimentacao import Movimentacao

# saida_venda fica de fora: quando uma consignação é criada, as unidades já saem de
# Produto.estoque_atual (via saida_consignacao). A venda só move unidades dentro da
# consignação (Consignacao.quantidade_atual, via baixar_estoque_consignacao) — registrar
# uma saida_venda aqui duplicaria a baixa no estoque central.
DIRECAO_ESTOQUE = {
    "entrada_manual": 1,
    "devolucao": 1,
    "saida_consignacao": -1,
}


def calcular_preco(custo, tipo_precificacao, valor_precificacao):
    custo = Decimal(custo)
    valor_precificacao = Decimal(valor_precificacao)
    if tipo_precificacao == "percentual":
        preco = custo * (Decimal("1") + valor_precificacao / Decimal("100"))
    elif tipo_precificacao == "fixo":
        preco = valor_precificacao
    else:
        raise ValueError(f"tipo_precificacao inválido: {tipo_precificacao}")
    return preco.quantize(Decimal("0.01"))


def registrar_movimentacao(produto, tipo, quantidade, usuario, descricao=None, referencia_tipo=None, referencia_id=None):
    """Grava uma Movimentacao e atualiza Produto.estoque_atual na mesma unidade de trabalho.

    Nunca deve ser feito separadamente — os dois precisam ficar sempre em sincronia.
    """
    if quantidade <= 0:
        raise ValueError("quantidade deve ser positiva")

    direcao = DIRECAO_ESTOQUE[tipo]
    novo_estoque = produto.estoque_atual + (direcao * quantidade)
    if novo_estoque < 0:
        raise ValueError(f"Estoque insuficiente para {produto.sku}: disponível={produto.estoque_atual}, solicitado={quantidade}")

    produto.estoque_atual = novo_estoque
    movimentacao = Movimentacao(
        produto_id=produto.id,
        tipo=tipo,
        quantidade=quantidade,
        usuario_id=usuario.id,
        descricao=descricao,
        referencia_tipo=referencia_tipo,
        referencia_id=referencia_id,
    )
    db.session.add(movimentacao)
    return movimentacao


def registrar_movimentacao_venda(produto, quantidade, usuario, descricao=None, referencia_id=None):
    """Grava a Movimentacao de auditoria de uma venda, sem tocar Produto.estoque_atual
    (essas unidades já saíram do estoque central quando a consignação foi criada — ver
    DIRECAO_ESTOQUE acima). A baixa real é em Consignacao.quantidade_atual, feita por
    baixar_estoque_consignacao().
    """
    if quantidade <= 0:
        raise ValueError("quantidade deve ser positiva")
    movimentacao = Movimentacao(
        produto_id=produto.id,
        tipo="saida_venda",
        quantidade=quantidade,
        usuario_id=usuario.id,
        descricao=descricao,
        referencia_tipo="venda",
        referencia_id=referencia_id,
    )
    db.session.add(movimentacao)
    return movimentacao


def baixar_estoque_consignacao(consignacao_id, quantidade):
    """UPDATE atômico condicional — evita duas vendas concorrentes venderem a mesma unidade.

    Retorna True se a baixa foi aplicada, False se não havia quantidade suficiente disponível
    (ex: outro vendedor da mesma equipe vendeu a unidade entre a validação do carrinho e a finalização).
    """
    resultado = db.session.execute(
        update(Consignacao)
        .where(Consignacao.id == consignacao_id, Consignacao.quantidade_atual >= quantidade, Consignacao.status == "ativa")
        .values(quantidade_atual=Consignacao.quantidade_atual - quantidade)
    )
    return resultado.rowcount == 1


def resolver_preco(equipe_id, produto):
    """Preço específico da equipe para o produto, se existir; senão o preço global do produto."""
    from app.models.preco_equipe_produto import PrecoEquipeProduto

    preco_equipe = PrecoEquipeProduto.query.filter_by(equipe_id=equipe_id, produto_id=produto.id).first()
    return preco_equipe.preco_venda if preco_equipe else produto.preco_venda


def gerar_pedido_numero():
    return f"PED-{secrets.token_hex(4).upper()}"


def gerar_senha_forte(tamanho=14):
    alfabeto = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%"
    return "".join(secrets.choice(alfabeto) for _ in range(tamanho))
