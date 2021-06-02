from app.blueprints.admin import sub_topic
from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.models.wiki import SubTopic, Topic, Tag
from flask import request

class QuestionEditForm(FlaskForm):
    question = StringField('Dúvida', validators=[DataRequired('Item obrigatório'), Length(min=5, max=256, message='A duvida deve conter um texto entre 5 e 256 caracteres')])
    answer = TextAreaField('Resposta', validators=[DataRequired('Item obrigatório'), Length(min=10, max=3000, message='A resposta deve conter um texto entre 10 e 3000 caracteres')])
    tag = QuerySelectMultipleField('Tag', allow_blank=False, query_factory= lambda : Tag.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    topic = QuerySelectField('Topico', allow_blank=False, query_factory= lambda : Topic.query, get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    sub_topic = QuerySelectField('Sub-Tópico', allow_blank=False, query_factory= lambda : SubTopic.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    # text = TextAreaField('Text', validators=[DataRequired('Item obrigatório'), Length(min=32, message='O campo texto deve conter pelo menos 32 caracteres')])
    # topic = QuerySelectField('Topico', validators=[DataRequired('Item obrigatório')], query_factory=lambda: Topic.query, get_label='name', allow_blank=False)
    approved = BooleanField('Aprovada')
    submit = SubmitField('Enviar')


class QuestionForm(FlaskForm):
    question = StringField('Dúvida', validators=[DataRequired('Item obrigatório'), Length(min=5, max=256, message='A duvida deve conter um texto entre 5 e 256 caracteres')])
    submit = SubmitField('Enviar')

class QuestionSearchForm(FlaskForm):
    q = StringField('Busca', validators=[DataRequired('Item Obrigatório'), Length(min=3, max=256, message='Busca limitada entre 3 e 256 caracteres')])
    # submit = SubmitField('Buscar')

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(QuestionSearchForm, self).__init__(*args, **kwargs)

class QuestionAnswerForm(FlaskForm):
    question = StringField('Dúvida', validators=[DataRequired('Item obrigatório'), Length(min=5, max=256, message='A duvida deve conter um texto entre 5 e 256 caracteres')])
    answer = TextAreaField('Resposta', validators=[DataRequired('Item obrigatório'), Length(min=10, max=3000, message='A descrição deve conter um texto entre 10 e 3000 caracteres')])
    tag = QuerySelectMultipleField('Tag', allow_blank=False, query_factory= lambda : Tag.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    topic = QuerySelectField('Topico', allow_blank=False, query_factory= lambda : Topic.query, get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    sub_topic = QuerySelectField('Sub-Tópico', allow_blank=False, query_factory= lambda : SubTopic.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    # text = TextAreaField('Text', validators=[DataRequired('Item obrigatório'), Length(min=32, message='O campo texto deve conter pelo menos 32 caracteres')])
    # topic = QuerySelectField('Topico', validators=[DataRequired('Item obrigatório')], query_factory=lambda: Topic.query, get_label='name', allow_blank=False)
    # approved = BooleanField('Aprovada')
    submit = SubmitField('Enviar')

class QuestionApproveForm(FlaskForm):
    question = StringField('Dúvida', validators=[DataRequired('Item obrigatório'), Length(min=5, max=256, message='A duvida deve conter um texto entre 5 e 256 caracteres')])
    answer = TextAreaField('Resposta', validators=[DataRequired('Item obrigatório'), Length(min=10, max=3000, message='A descrição deve conter um texto entre 10 e 3000 caracteres')])
    tag = QuerySelectMultipleField('Tag', allow_blank=False, query_factory= lambda : Tag.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    topic = QuerySelectField('Topico', allow_blank=False, query_factory= lambda : Topic.query, get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    sub_topic = QuerySelectField('Sub-Tópico', allow_blank=False, query_factory= lambda : SubTopic.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    # text = TextAreaField('Text', validators=[DataRequired('Item obrigatório'), Length(min=32, message='O campo texto deve conter pelo menos 32 caracteres')])
    # topic = QuerySelectField('Topico', validators=[DataRequired('Item obrigatório')], query_factory=lambda: Topic.query, get_label='name', allow_blank=False)
    approve = BooleanField('Aprovada')
    submit = SubmitField('Enviar')

class CreateQuestion(FlaskForm):
    question = TextAreaField('Dúvida?', validators=[DataRequired('Item Obrigatório'), Length(min=5, max=256, message='A dúvida deve conter entre 5 e 256 caracteres')])
    topic = QuerySelectField('Topico', allow_blank=False, query_factory= lambda: Topic.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    submit = SubmitField('Enviar')