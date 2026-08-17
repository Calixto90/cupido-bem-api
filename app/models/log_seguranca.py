from datetime import datetime, timezone

from app.extensions import db

EVENTOS_SEGURANCA = ("login_falho", "login_sucesso", "permissao_negada", "rate_limit_excedido")


class LogSeguranca(db.Model):
    __tablename__ = "logs_seguranca"

    id = db.Column(db.Integer, primary_key=True)
    evento = db.Column(db.Enum(*EVENTOS_SEGURANCA, name="evento_seguranca"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    email_tentativa = db.Column(db.String(120), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    rota = db.Column(db.String(255), nullable=True)
    detalhes = db.Column(db.Text, nullable=True)
    data_evento = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    usuario = db.relationship("User")

    def __repr__(self):
        return f"<LogSeguranca {self.evento} em={self.data_evento}>"
