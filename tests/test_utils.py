from decimal import Decimal

import pytest

from app.utils import baixar_estoque_consignacao, calcular_preco, registrar_movimentacao


def test_calcular_preco_percentual():
    assert calcular_preco(10, "percentual", 100) == Decimal("20.00")
    assert calcular_preco(15, "percentual", 20) == Decimal("18.00")


def test_calcular_preco_fixo_ignora_custo():
    # "fixo" define o preço de venda diretamente, não soma ao custo (confirmado no doc original).
    assert calcular_preco(999, "fixo", 25) == Decimal("25.00")


def test_registrar_movimentacao_entrada_aumenta_estoque(db, produto, admin_user):
    estoque_antes = produto.estoque_atual
    registrar_movimentacao(produto, "entrada_manual", 10, admin_user)
    assert produto.estoque_atual == estoque_antes + 10


def test_registrar_movimentacao_saida_consignacao_diminui_estoque(db, produto, admin_user):
    estoque_antes = produto.estoque_atual
    registrar_movimentacao(produto, "saida_consignacao", 10, admin_user)
    assert produto.estoque_atual == estoque_antes - 10


def test_registrar_movimentacao_recusa_estoque_insuficiente(db, produto, admin_user):
    with pytest.raises(ValueError):
        registrar_movimentacao(produto, "saida_consignacao", produto.estoque_atual + 1, admin_user)


def test_baixar_estoque_consignacao_sucesso(db, consignacao_ativa):
    ok = baixar_estoque_consignacao(consignacao_ativa.id, 4)
    db.session.commit()
    assert ok is True
    db.session.refresh(consignacao_ativa)
    assert consignacao_ativa.quantidade_atual == 6


def test_baixar_estoque_consignacao_falha_quando_insuficiente(db, consignacao_ativa):
    ok = baixar_estoque_consignacao(consignacao_ativa.id, 999)
    db.session.rollback()
    assert ok is False
    db.session.refresh(consignacao_ativa)
    assert consignacao_ativa.quantidade_atual == 10


def test_baixar_estoque_consignacao_segunda_baixa_nao_pode_vender_o_que_ja_foi_vendido(db, consignacao_ativa):
    """Simula duas vendas concorrentes da mesma equipe disputando as últimas unidades."""
    primeira_ok = baixar_estoque_consignacao(consignacao_ativa.id, 7)
    segunda_ok = baixar_estoque_consignacao(consignacao_ativa.id, 7)
    db.session.commit()

    assert primeira_ok is True
    assert segunda_ok is False  # só restavam 3 unidades depois da primeira baixa
    db.session.refresh(consignacao_ativa)
    assert consignacao_ativa.quantidade_atual == 3
