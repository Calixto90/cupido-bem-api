from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

from app.models.produto import TIPOS_PRECIFICACAO


class ProdutoForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=150)])
    sku = StringField("SKU", validators=[DataRequired(), Length(max=50)])
    custo = DecimalField("Custo", validators=[DataRequired(), NumberRange(min=0)], places=2)
    tipo_precificacao = SelectField("Tipo de precificação", choices=[(t, t) for t in TIPOS_PRECIFICACAO], validators=[DataRequired()])
    valor_precificacao = DecimalField("Valor (markup % ou preço fixo)", validators=[DataRequired(), NumberRange(min=0)], places=2)
    estoque_minimo = IntegerField("Estoque mínimo", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField("Salvar")


class EntradaEstoqueForm(FlaskForm):
    quantidade = IntegerField("Quantidade", validators=[DataRequired(), NumberRange(min=1)])
    descricao = StringField("Descrição (opcional)", validators=[Length(max=255)])
    submit = SubmitField("Registrar entrada")
