from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class ConsignacaoForm(FlaskForm):
    equipe_id = SelectField("Equipe", coerce=int, validators=[DataRequired()])
    produto_id = SelectField("Produto", coerce=int, validators=[DataRequired()])
    quantidade = IntegerField("Quantidade", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Criar consignação")
