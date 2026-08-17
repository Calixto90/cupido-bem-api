from datetime import datetime, timezone

from app.extensions import db


class Venda(db.Model):
    __tablename__ = "vendas"

    id = db.Column(db.Integer, primary_key=True)
    pedido_numero = db.Column(db.String(40), unique=True, nullable=False, index=True)

    nome_cliente = db.Column(db.String(150), nullable=False)
    telefone_cliente = db.Column(db.String(30), nullable=False)
    email_cliente = db.Column(db.String(120), nullable=True)
    obs_cliente = db.Column(db.Text, nullable=True)

    nome_destinatario = db.Column(db.String(150), nullable=False)
    telefone_destinatario = db.Column(db.String(30), nullable=True)
    endereco_destinatario = db.Column(db.Text, nullable=False)
    obs_destinatario = db.Column(db.Text, nullable=True)

    total_venda = db.Column(db.Numeric(10, 2), nullable=False)
    data_venda = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    criado_por_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    criado_por = db.relationship("User")
    itens = db.relationship("ItemVenda", back_populates="venda", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Venda {self.pedido_numero} total={self.total_venda}>"


class ItemVenda(db.Model):
    __tablename__ = "itens_venda"

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey("vendas.id"), nullable=False)
    consignacao_id = db.Column(db.Integer, db.ForeignKey("consignacoes.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    venda = db.relationship("Venda", back_populates="itens")
    consignacao = db.relationship("Consignacao", back_populates="itens_venda")

    def __repr__(self):
        return f"<ItemVenda venda={self.venda_id} consignacao={self.consignacao_id} qtd={self.quantidade}>"
