"""Popula o banco com dados de demonstração: um usuário por perfil, duas equipes,
alguns produtos e uma consignação ativa. Senhas são geradas aleatoriamente e
gravadas em seed_credentials_LOCAL.txt (gitignored) — nunca no código-fonte.

Uso: flask --app wsgi.py shell -c "exec(open('scripts/seed.py').read())"
ou, mais simples: python scripts/seed.py (roda dentro do contexto da app).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.consignacao import Consignacao
from app.models.equipe import Equipe
from app.models.produto import Produto
from app.models.user import User
from app.utils import calcular_preco, gerar_senha_forte, registrar_movimentacao


def seed():
    app = create_app()
    with app.app_context():
        if User.query.first():
            print("Banco já tem dados — seed abortado para não duplicar. Limpe o banco antes se quiser recriar.")
            return

        credenciais = []

        def criar_usuario(nome, email, role, equipe_id=None):
            senha = gerar_senha_forte()
            usuario = User(nome=nome, email=email, role=role, equipe_id=equipe_id, ativo=True)
            usuario.set_senha(senha)
            db.session.add(usuario)
            credenciais.append((email, senha, role))
            return usuario

        admin = criar_usuario("Administrador", "admin@cupidodobem.com", "admin")
        gerente = criar_usuario("Gerente Geral", "gerente@cupidodobem.com", "gerente")
        estoquista = criar_usuario("Estoquista", "estoquista@cupidodobem.com", "estoquista")
        caixa_user = criar_usuario("Caixa", "caixa@cupidodobem.com", "caixa")
        db.session.flush()

        equipe_a = Equipe(nome="Equipe Rosa", descricao="Equipe de demonstração A")
        equipe_b = Equipe(nome="Equipe Vermelha", descricao="Equipe de demonstração B")
        db.session.add_all([equipe_a, equipe_b])
        db.session.flush()

        vendedor1 = criar_usuario("Vendedor Um", "vendedor1@cupidodobem.com", "vendedor", equipe_a.id)
        vendedor2 = criar_usuario("Vendedor Dois", "vendedor2@cupidodobem.com", "vendedor", equipe_a.id)
        vendedor3 = criar_usuario("Vendedor Três", "vendedor3@cupidodobem.com", "vendedor", equipe_b.id)
        db.session.flush()

        produtos_dados = [
            ("Urso de Pelúcia P", "URS-P-001", 15.00, "percentual", 100, 20),
            ("Buquê de Rosas", "BUQ-ROS-001", 25.00, "fixo", 60.00, 15),
            ("Caixa de Bombons", "BOM-CX-001", 18.00, "percentual", 80, 30),
        ]
        produtos = []
        for nome, sku, custo, tipo, valor, estoque_min in produtos_dados:
            preco = calcular_preco(custo, tipo, valor)
            produto = Produto(
                nome=nome,
                sku=sku,
                custo=custo,
                tipo_precificacao=tipo,
                valor_precificacao=valor,
                preco_venda=preco,
                estoque_minimo=estoque_min,
                estoque_atual=0,
            )
            db.session.add(produto)
            produtos.append(produto)
        db.session.flush()

        for produto in produtos:
            registrar_movimentacao(produto, "entrada_manual", 100, admin, descricao="Estoque inicial de demonstração")
        db.session.flush()

        consignacao = Consignacao(
            equipe_id=equipe_a.id,
            produto_id=produtos[0].id,
            quantidade_inicial=20,
            quantidade_atual=20,
            status="ativa",
            criado_por_user_id=gerente.id,
        )
        db.session.add(consignacao)
        registrar_movimentacao(
            produtos[0],
            "saida_consignacao",
            20,
            gerente,
            descricao=f"Consignação de demonstração para {equipe_a.nome}",
            referencia_tipo="consignacao",
        )

        db.session.commit()

        caminho_credenciais = os.path.join(os.path.dirname(__file__), "..", "seed_credentials_LOCAL.txt")
        with open(caminho_credenciais, "w", encoding="utf-8") as f:
            f.write("Credenciais de demonstração — NAO versionar, NAO usar em produção sem trocar a senha.\n\n")
            for email, senha, role in credenciais:
                f.write(f"{role:12s} | {email:35s} | {senha}\n")

        print(f"Seed concluído. Credenciais gravadas em: {os.path.abspath(caminho_credenciais)}")


if __name__ == "__main__":
    seed()
