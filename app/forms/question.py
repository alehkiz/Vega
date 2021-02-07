from operator import sub
from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models.wiki import Topic
from flask import request

class QuestionForm(FlaskForm):
    question = StringField('Dúvida', validators=[DataRequired('Item obrigatório'), Length(min=5, max=256, message='A duvida deve conter um texto entre 5 e 256 caracteres')])
    answer = TextAreaField('Resposta', validators=[DataRequired('Item obrigatório'), Length(min=10, max=10000, message='A descrição deve conter um texto entre 10 e 10000 caracteres')])
    # text = TextAreaField('Text', validators=[DataRequired('Item obrigatório'), Length(min=32, message='O campo texto deve conter pelo menos 32 caracteres')])
    # topic = QuerySelectField('Topico', validators=[DataRequired('Item obrigatório')], query_factory=lambda: Topic.query, get_label='name', allow_blank=False)
    submit = SubmitField('Enviar')

class QuestionSearchForm(FlaskForm):
    q = StringField('Busca', validators=[DataRequired('Item Obrigatório'), Length(min=3, max=256, message='Busca limitada entre 3 e 256 caracteres')])
    # submit = SubmitField('Buscar')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(FlaskForm, self).__init__(*args, **kwargs)