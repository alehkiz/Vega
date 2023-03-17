from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, BooleanField, MultipleFileField, FieldList
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.models.transactions import Parameter, TransactionType
from app.models.wiki import SubTopic, Topic, Tag
from app.models.security import User
from flask import request


class TransactionForm(FlaskForm):
    transaction = StringField('Transação', validators=[DataRequired('Item obrigatório'), Length(min=4, max=4, message='A transação deve ter exatamente 4 caracteres')])
    parameter = QuerySelectMultipleField('Parametros', allow_blank=False, query_factory= lambda : Parameter.query, get_label = 'type')
    # option = QuerySelectMultipleField('Parametros', allow_blank=False, query_factory= lambda : TransactionParameter.query, get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    # tag = QuerySelectMultipleField('Tag', allow_blank=False, query_factory= lambda : Tag.query.order_by(Tag.name.asc()), get_label='name', validators=[DataRequired('Item Obrigatório')])
    description = TextAreaField('Descrição', validators=[DataRequired('Item obrigatório'), Length(min=8, max=540, message='A descrição deve ter entre 8 e 540 caracteres')])
    type = QuerySelectMultipleField('Tipo', allow_blank=False, query_factory= lambda : TransactionType.query, get_label = 'type', validators = [DataRequired('Item Obrigatório')])
    topic = QuerySelectMultipleField('Topico', allow_blank=False, query_factory= lambda : Topic.query.filter(Topic.selectable == True), get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    sub_topics = QuerySelectMultipleField('Sub-Tópico', allow_blank=True, query_factory= lambda : SubTopic.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    submit = SubmitField('Salvar')
    prints = SubmitField('Prints')


class TransactionOptionForm(FlaskForm):
    transaction = StringField('Transação', render_kw={'disabled':''})
    options = FieldList(StringField('Opção'), min_entries=1)
    description = TextAreaField('Descrição')
    submit = SubmitField('Salvar')

class TransactionScreenForn(FlaskForm):
    transaction = StringField('Transação', render_kw={'disabled':''})
    files = MultipleFileField("Arquivos")
    submit = SubmitField('Salvar')
    