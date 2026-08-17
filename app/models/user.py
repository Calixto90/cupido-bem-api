from datetime import datetime, timezone

import bcrypt
from flask_login import UserMixin

from app.extensions import db

ROLES = ("admin", "gerente", "vendedor", "caixa", "estoquista")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(*ROLES, name="user_role"), nullable=False)
    equipe_id = db.Column(db.Integer, db.ForeignKey("equipes.id"), nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    ultimo_login = db.Column(db.DateTime, nullable=True)

    equipe = db.relationship("Equipe", back_populates="membros", foreign_keys=[equipe_id])

    def set_senha(self, senha_texto):
        self.senha_hash = bcrypt.hashpw(senha_texto.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_senha(self, senha_texto):
        return bcrypt.checkpw(senha_texto.encode("utf-8"), self.senha_hash.encode("utf-8"))

    def is_role(self, *roles):
        return self.role in roles

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.ativo

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
