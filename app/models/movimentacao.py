from datetime import datetime, timezone

from app.extensions import db

TIPOS_MOVIMENTACAO = ("entrada_manual", "saida_consignacao", "saida_venda", "devolucao")


class Movimentacao(db.Model):
    __tablename__ = "movimentacoes"

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    tipo = db.Column(db.Enum(*TIPOS_MOVIMENTACAO, name="tipo_movimentacao"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    data_movimento = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    usuario_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    referencia_tipo = db.Column(db.String(30), nullable=True)
    referencia_id = db.Column(db.Integer, nullable=True)

    produto = db.relationship("Produto")
    usuario = db.relationship("User")

    def __repr__(self):
        return f"<Movimentacao {self.tipo} produto={self.produto_id} qtd={self.quantidade}>"
