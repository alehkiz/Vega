from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.models.app import FilePDFType
from app.models.wiki import Topic
from flask import request

class FilePDFTypeEditForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired('Item obrigatório'), Length(min=3, max=32, message='A marcação deve conter um texto entre 5 e 256 caracteres')])
    active = BooleanField('Ativo')
    url_route = StringField('Nome', validators=[DataRequired('Item obrigatório'), Length(min=3, max=32, message='A marcação deve conter um texto entre 5 e 256 caracteres')])
    # answer = TextAreaField('Resposta', validators=[DataRequired('Item obrigatório'), Length(min=10, max=10000, message='A descrição deve conter um texto entre 10 e 10000 caracteres')])
    # tag = QuerySelectMultipleField('Topic', allow_blank=False, query_factory= lambda : Topic.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    # topic = QuerySelectField('Topico', allow_blank=False, query_factory= lambda : Topic.query, get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    # text = TextAreaField('Text', validators=[DataRequired('Item obrigatório'), Length(min=32, message='O campo texto deve conter pelo menos 32 caracteres')])
    # topic = QuerySelectField('Topico', validators=[DataRequired('Item obrigatório')], query_factory=lambda: Topic.query, get_label='name', allow_blank=False)
    submit = SubmitField('Enviar')

class FilePDFTypeFilter(FlaskForm):
    type = QuerySelectMultipleField('Tipo', 
                allow_blank=False, 
                query_factory= lambda : FilePDFType.query, 
                get_label='name')
    topic = QuerySelectMultipleField('Tópico',
                allow_blank=False,
                query_factory= lambda : Topic.query,
                get_label='name'
                )
    approved = BooleanField('Aprovada')
    submit = SubmitField('Filtrar')