from datetime import datetime, timezone

from app.extensions import db


class Equipe(db.Model):
    __tablename__ = "equipes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    membros = db.relationship("User", back_populates="equipe", foreign_keys="User.equipe_id")
    consignacoes = db.relationship("Consignacao", back_populates="equipe")
    precos = db.relationship("PrecoEquipeProduto", back_populates="equipe")
    pagamentos = db.relationship("PagamentoEquipe", back_populates="equipe")

    def tem_consignacao_ativa(self):
        return any(c.status == "ativa" for c in self.consignacoes)

    def __repr__(self):
        return f"<Equipe {self.nome}>"
