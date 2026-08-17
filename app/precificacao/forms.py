from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from app.models.produto import TIPOS_PRECIFICACAO


class PrecificacaoIndividualForm(FlaskForm):
    tipo_precificacao = SelectField("Tipo", choices=[(t, t) for t in TIPOS_PRECIFICACAO], validators=[DataRequired()])
    valor_precificacao = DecimalField("Valor (markup % ou preço fixo)", validators=[DataRequired(), NumberRange(min=0)], places=2)
    submit = SubmitField("Salvar preço")


class PrecificacaoLoteForm(FlaskForm):
    produtos = SelectMultipleField("Produtos", coerce=int, validators=[DataRequired()])
    tipo_precificacao = SelectField("Tipo", choices=[(t, t) for t in TIPOS_PRECIFICACAO], validators=[DataRequired()])
    valor_precificacao = DecimalField("Valor (markup % ou preço fixo)", validators=[DataRequired(), NumberRange(min=0)], places=2)
    submit = SubmitField("Aplicar em lote")
