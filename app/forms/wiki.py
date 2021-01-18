from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

class ArticleForm(FlaskForm):
    title = StringField('Titulo', validators=[DataRequired('Item obrigatório'), Length(min=5, max=32, message='O título deve conter um texto entre 5 e 32 caracteres')])
    description = StringField('Descrição', validators=[DataRequired('Item obrigatório'), Length(min=10, max=128, message='A descrição deve conter um texto entre 10 e 128 caracteres')])
    text = TextAreaField('Text', validators=[DataRequired('Item obrigatório'), Length(min=32, message='O campo texto deve conter pelo menos 32 caracteres')])
    submit = SubmitField('Enviar')
    