from datetime import datetime, timezone

from app.extensions import db


class PagamentoEquipe(db.Model):
    __tablename__ = "pagamentos_equipe"

    id = db.Column(db.Integer, primary_key=True)
    equipe_id = db.Column(db.Integer, db.ForeignKey("equipes.id"), nullable=False)
    valor_pago = db.Column(db.Numeric(10, 2), nullable=False)
    data_pagamento = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    observacao = db.Column(db.Text, nullable=True)
    registrado_por_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    equipe = db.relationship("Equipe", back_populates="pagamentos")
    registrado_por = db.relationship("User")

    def __repr__(self):
        return f"<PagamentoEquipe equipe={self.equipe_id} valor={self.valor_pago}>"
