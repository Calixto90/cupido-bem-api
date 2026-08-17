from datetime import datetime, timezone

from app.extensions import db

STATUS_CONSIGNACAO = ("ativa", "vendida_total", "cancelada")


class Consignacao(db.Model):
    __tablename__ = "consignacoes"

    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey("equipes.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    quantidade_inicial = db.Column(db.Integer, nullable=False)
    quantidade_atual = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(*STATUS_CONSIGNACAO, name="status_consignacao"), nullable=False, default="ativa")
    data_retirada = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    criado_por_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    equipe = db.relationship("Equipe", back_populates="consignacoes")
    produto = db.relationship("Produto")
    criado_por = db.relationship("User")
    itens_venda = db.relationship("ItemVenda", back_populates="consignacao")

    def __repr__(self):
        return f"<Consignacao {self.id} equipe={self.equipe_id} produto={self.produto_id} status={self.status}>"
