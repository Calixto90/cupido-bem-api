from datetime import datetime, timezone

from app.extensions import db

TIPOS_PRECIFICACAO = ("percentual", "fixo")


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    custo = db.Column(db.Numeric(10, 2), nullable=False)
    tipo_precificacao = db.Column(db.Enum(*TIPOS_PRECIFICACAO, name="tipo_precificacao"), nullable=False)
    valor_precificacao = db.Column(db.Numeric(10, 2), nullable=False)
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False)
    estoque_minimo = db.Column(db.Integer, nullable=False, default=0)
    estoque_atual = db.Column(db.Integer, nullable=False, default=0)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Produto {self.sku} {self.nome}>"

    @property
    def estoque_baixo(self):
        return self.estoque_atual < self.estoque_minimo
