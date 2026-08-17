from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

from app.models.user import ROLES


class UsuarioForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = SelectField("Perfil", choices=[(r, r) for r in ROLES], validators=[DataRequired()])
    equipe_id = SelectField("Equipe (só para vendedor)", coerce=int, validators=[Optional()])
    senha = PasswordField("Senha (deixe em branco para manter)", validators=[Optional(), Length(min=6)])
    ativo = BooleanField("Ativo", default=True)
    submit = SubmitField("Salvar")
