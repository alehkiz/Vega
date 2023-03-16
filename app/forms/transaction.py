from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.models.transactions import TransactionParameter, TransactionType
from app.models.wiki import SubTopic, Topic, Tag
from app.models.security import User
from flask import request


class TransactionForm(FlaskForm):
    transaction = TextAreaField('Transação', validators=[DataRequired('Item obrigatório'), Length(min=4, max=4, message='A transação deve ter exatamente 4 caracteres')])
    parameter = QuerySelectMultipleField('Parametros', allow_blank=False, query_factory= lambda : TransactionParameter.query, get_label = 'type')
    # option = QuerySelectMultipleField('Parametros', allow_blank=False, query_factory= lambda : TransactionParameter.query, get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    # tag = QuerySelectMultipleField('Tag', allow_blank=False, query_factory= lambda : Tag.query.order_by(Tag.name.asc()), get_label='name', validators=[DataRequired('Item Obrigatório')])
    type = QuerySelectMultipleField('Tipo', allow_blank=False, query_factory= lambda : TransactionType.query, get_label = 'type', validators = [DataRequired('Item Obrigatório')])
    topic = QuerySelectMultipleField('Topico', allow_blank=False, query_factory= lambda : Topic.query.filter(Topic.selectable == True), get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    sub_topic = QuerySelectMultipleField('Sub-Tópico', allow_blank=True, query_factory= lambda : SubTopic.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    submit = SubmitField('Enviar')

class TransactionOptionForm(FlaskForm):
    transaction = TextAreaField('Transação', validators=[DataRequired('Item obrigatório'), Length(min=4, max=4, message='A transação deve ter exatamente 4 caracteres')],render_kw={'disabled':''})
    
    