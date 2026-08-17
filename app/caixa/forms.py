from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class PagamentoForm(FlaskForm):
    equipe_id = SelectField("Equipe", coerce=int, validators=[DataRequired()])
    valor_pago = DecimalField("Valor pago", validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    observacao = TextAreaField("Observação")
    submit = SubmitField("Registrar pagamento")
