from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.models.wiki import SubTopic, Topic, Tag
from app.models.security import User
from flask import request


class TransactionEditForm(FlaskForm):
    transaction = TextAreaField('Transação', validators=[DataRequired('Item obrigatório'), Length(min=4, max=4, message='A transação deve ter exatamente 4 caracteres')])
    parameter = TextAreaField('Parametro', validators=[DataRequired('Item obrigatório'), Length(min=1, max=10, message='O parametro deve ter entre 1 e 10 caracteres')])
    option = TextAreaField('Opção', validators=[DataRequired('Item obrigatório'), Length(min=1, max=10, message='A opção deve ter entre 1 e 10 caracteres')])
    tag = QuerySelectMultipleField('Tag', allow_blank=False, query_factory= lambda : Tag.query.order_by(Tag.name.asc()), get_label='name', validators=[DataRequired('Item Obrigatório')])
    topic = QuerySelectMultipleField('Topico', allow_blank=False, query_factory= lambda : Topic.query.filter(Topic.selectable == True), get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    sub_topic = QuerySelectMultipleField('Sub-Tópico', allow_blank=True, query_factory= lambda : SubTopic.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    submit = SubmitField('Enviar')