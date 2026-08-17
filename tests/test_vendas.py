import json
import re


def login(client, email, senha):
    client.get("/auth/login")  # garante que a sessão existe antes do POST
    return client.post("/auth/login", data={"email": email, "senha": senha, "submit": "Entrar"})


def _csrf_meta(html_bytes):
    match = re.search(rb'name="csrf-token" content="([^"]+)"', html_bytes)
    return match.group(1).decode()


def test_fluxo_completo_de_venda_atualiza_estoque_e_caixa(client, db, vendedor_user, consignacao_ativa, equipe):
    login(client, "vendedor@teste.com", "senha123")

    pagina = client.get("/vendas/")
    csrf = _csrf_meta(pagina.data)
    headers = {"X-CSRFToken": csrf, "Content-Type": "application/json"}

    payload = {
        "itens": [{"consignacao_id": consignacao_ativa.id, "quantidade": 3}],
        "comprador": {"nome": "Cliente Teste", "telefone": "11999999999", "email": "", "observacao": ""},
        "destinatario": {"nome": "Destinatário Teste", "telefone": "", "endereco": "Rua Teste, 1", "observacao": ""},
    }
    resp = client.post("/vendas/checkout/finalizar", data=json.dumps(payload), headers=headers)
    assert resp.status_code == 200
    corpo = resp.get_json()
    assert corpo["pedido_numero"].startswith("PED-")

    db.session.refresh(consignacao_ativa)
    assert consignacao_ativa.quantidade_atual == 7
    assert consignacao_ativa.status == "ativa"


def test_venda_recusa_quantidade_maior_que_disponivel(client, db, vendedor_user, consignacao_ativa):
    login(client, "vendedor@teste.com", "senha123")
    pagina = client.get("/vendas/")
    csrf = _csrf_meta(pagina.data)
    headers = {"X-CSRFToken": csrf, "Content-Type": "application/json"}

    payload = {
        "itens": [{"consignacao_id": consignacao_ativa.id, "quantidade": 999}],
        "comprador": {"nome": "Cliente Teste", "telefone": "11999999999"},
        "destinatario": {"nome": "Destinatário Teste", "endereco": "Rua Teste, 1"},
    }
    resp = client.post("/vendas/checkout/finalizar", data=json.dumps(payload), headers=headers)
    assert resp.status_code == 409

    db.session.refresh(consignacao_ativa)
    assert consignacao_ativa.quantidade_atual == 10  # nada foi decrementado


def test_venda_zera_consignacao_e_muda_status_para_vendida_total(client, db, vendedor_user, consignacao_ativa):
    login(client, "vendedor@teste.com", "senha123")
    pagina = client.get("/vendas/")
    csrf = _csrf_meta(pagina.data)
    headers = {"X-CSRFToken": csrf, "Content-Type": "application/json"}

    payload = {
        "itens": [{"consignacao_id": consignacao_ativa.id, "quantidade": 10}],
        "comprador": {"nome": "Cliente Teste", "telefone": "11999999999"},
        "destinatario": {"nome": "Destinatário Teste", "endereco": "Rua Teste, 1"},
    }
    resp = client.post("/vendas/checkout/finalizar", data=json.dumps(payload), headers=headers)
    assert resp.status_code == 200

    db.session.refresh(consignacao_ativa)
    assert consignacao_ativa.quantidade_atual == 0
    assert consignacao_ativa.status == "vendida_total"
