import pytest

from app import create_app
from app.extensions import db as _db
from app.models.consignacao import Consignacao
from app.models.equipe import Equipe
from app.models.produto import Produto
from app.models.user import User
from app.utils import calcular_preco


@pytest.fixture
def app():
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user(db):
    user = User(nome="Admin", email="admin@teste.com", role="admin")
    user.set_senha("senha123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def vendedor_user(db, equipe):
    user = User(nome="Vendedor", email="vendedor@teste.com", role="vendedor", equipe_id=equipe.id)
    user.set_senha("senha123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def equipe(db):
    equipe = Equipe(nome="Equipe Teste")
    db.session.add(equipe)
    db.session.commit()
    return equipe


@pytest.fixture
def produto(db):
    custo = 10
    preco = calcular_preco(custo, "percentual", 100)
    produto = Produto(
        nome="Produto Teste",
        sku="SKU-TESTE",
        custo=custo,
        tipo_precificacao="percentual",
        valor_precificacao=100,
        preco_venda=preco,
        estoque_minimo=5,
        estoque_atual=50,
    )
    db.session.add(produto)
    db.session.commit()
    return produto


@pytest.fixture
def consignacao_ativa(db, equipe, produto, admin_user):
    consignacao = Consignacao(
        equipe_id=equipe.id,
        produto_id=produto.id,
        quantidade_inicial=10,
        quantidade_atual=10,
        status="ativa",
        criado_por_user_id=admin_user.id,
    )
    db.session.add(consignacao)
    db.session.commit()
    return consignacao
