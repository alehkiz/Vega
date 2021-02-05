from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models.wiki import Topic

class QuestionForm(FlaskForm):
    question = StringField('Dúvida', validators=[DataRequired('Item obrigatório'), Length(min=5, max=256, message='A duvida deve conter um texto entre 5 e 256 caracteres')])
    answer = TextAreaField('Resposta', validators=[DataRequired('Item obrigatório'), Length(min=10, max=10000, message='A descrição deve conter um texto entre 10 e 10000 caracteres')])
    # text = TextAreaField('Text', validators=[DataRequired('Item obrigatório'), Length(min=32, message='O campo texto deve conter pelo menos 32 caracteres')])
    # topic = QuerySelectField('Topico', validators=[DataRequired('Item obrigatório')], query_factory=lambda: Topic.query, get_label='name', allow_blank=False)
    submit = SubmitField('Enviar')
    