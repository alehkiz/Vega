from flask_wtf import FlaskForm
from sqlalchemy.orm import query
from sqlalchemy.orm.query import Query
from app.models.notifier import Notifier, NotifierPriority, NotifierPriority, NotifierStatus
from app.models.wiki import Topic
from wtforms.validators import DataRequired, Length
from wtforms import TextAreaField, StringField, SubmitField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

class NotifierForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired('Item obriatório'), Length(min=5, max=128, message='O titulo deve conster entre 5 e 128 caracteres')])
    content = TextAreaField('Conteúdo', validators=[DataRequired('Item obrigatório'), Length(min=5, max=500, message='O titulo deve conster entre 5 e 500 caracteres')])
    status = QuerySelectField('Status', allow_blank=False, query_factory=lambda: NotifierStatus.query, get_label='status',validators=[DataRequired('Item obrigatório')])
    priority = QuerySelectField('Prioridade', allow_blank=False, query_factory=lambda: NotifierPriority.query, get_label='priority', validators=[DataRequired('Item obrigatório')])
    topic = QuerySelectField('Topico', allow_blank=False, query_factory=lambda: Topic.query.filter(Topic.active == True), get_label='name', validators=[DataRequired('Item obrigarório')])
    submit = SubmitField('Enviar')