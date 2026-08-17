from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class EquipeForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=100)])
    descricao = TextAreaField("Descrição", validators=[Length(max=2000)])
    vendedores = SelectMultipleField("Vendedores (2 a 3)", coerce=int)
    submit = SubmitField("Salvar")

    def validate_vendedores(self, field):
        quantidade = len(field.data) if field.data else 0
        if not (2 <= quantidade <= 3):
            from wtforms import ValidationError

            raise ValidationError("Selecione entre 2 e 3 vendedores para a equipe.")
