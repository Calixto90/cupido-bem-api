from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")


class AlterarSenhaForm(FlaskForm):
    senha_atual = PasswordField("Senha atual", validators=[DataRequired()])
    nova_senha = PasswordField("Nova senha", validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField("Confirmar nova senha", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Alterar senha")
