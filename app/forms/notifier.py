from flask_wtf import FlaskForm
from sqlalchemy.orm import query
from sqlalchemy.orm.query import Query
from app.models.notifier import Notifier, NotifierLevel, NotifierPriority, NotifierPriority, NotifierStatus
from app.models.wiki import SubTopic, Topic
from wtforms.validators import DataRequired, Length
from wtforms import TextAreaField, StringField, SubmitField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

class NotifierForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired('Item obrigatório'), Length(min=5, max=25, message='O titulo deve conster entre 5 e 40 caracteres')])
    content = TextAreaField('Conteúdo', validators=[DataRequired('Item obrigatório'), Length(min=5, max=250, message='O titulo deve conster entre 5 e 150 caracteres')])
    status = QuerySelectField('Status', allow_blank=False, query_factory=lambda: NotifierStatus.query, get_label='status',validators=[DataRequired('Item obrigatório')])
    priority = QuerySelectField('Prioridade', allow_blank=False, query_factory=lambda: NotifierPriority.query.order_by(NotifierPriority.order.asc()), get_label='priority', validators=[DataRequired('Item obrigatório')])
    level = QuerySelectField('Nível', allow_blank=False, query_factory=lambda: NotifierLevel.query, get_label='level_translate', validators=[DataRequired('Item obrigatório')])
    # topic = QuerySelectField('Topico', allow_blank=False, query_factory=lambda: Topic.query.filter(Topic.active == True), get_label='name', validators=[DataRequired('Item obrigarório')])
    sub_topics = QuerySelectMultipleField('Topicos', allow_blank=False, query_factory= lambda : SubTopic.query, get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    topics = QuerySelectMultipleField('Topicos', allow_blank=False, query_factory= lambda : Topic.query.filter(Topic.selectable == True), get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    autoload = BooleanField('Carregar automático')
    submit = SubmitField('Enviar')