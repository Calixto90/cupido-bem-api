from datetime import datetime, timezone

from app.extensions import db
from app.models.produto import TIPOS_PRECIFICACAO


class PrecoEquipeProduto(db.Model):
    __tablename__ = "precos_equipe_produto"
    __table_args__ = (db.UniqueConstraint("equipe_id", "produto_id", name="uq_equipe_produto"),)

    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey("equipes.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    tipo_precificacao = db.Column(db.Enum(*TIPOS_PRECIFICACAO, name="tipo_precificacao_equipe"), nullable=False)
    valor_precificacao = db.Column(db.Numeric(10, 2), nullable=False)
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False)
    atualizado_em = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    atualizado_por_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    equipe = db.relationship("Equipe", back_populates="precos")
    produto = db.relationship("Produto")
    atualizado_por = db.relationship("User")

    def __repr__(self):
        return f"<PrecoEquipeProduto equipe={self.equipe_id} produto={self.produto_id}>"
