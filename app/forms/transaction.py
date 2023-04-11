from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, BooleanField, MultipleFileField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.models.transaction import Parameter, TransactionFinality, TransactionOption, TransactionType
from app.models.wiki import SubTopic, Topic, Tag
from app.models.security import User
from flask import request


class TransactionForm(FlaskForm):
    transaction = StringField('Transação', validators=[DataRequired('Item obrigatório'), Length(min=4, max=4, message='A transação deve ter exatamente 4 caracteres')])
    parameter = QuerySelectMultipleField('Parametros', allow_blank=False, query_factory= lambda : Parameter.query, get_label = 'type')
    # option = QuerySelectMultipleField('Parametros', allow_blank=False, query_factory= lambda : TransactionParameter.query, get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    # tag = QuerySelectMultipleField('Tag', allow_blank=False, query_factory= lambda : Tag.query.order_by(Tag.name.asc()), get_label='name', validators=[DataRequired('Item Obrigatório')])
    description = TextAreaField('Descrição', validators=[DataRequired('Item obrigatório'), Length(min=8, max=540, message='A descrição deve ter entre 8 e 540 caracteres')])
    type = QuerySelectMultipleField('Tipos', allow_blank=False, query_factory= lambda : TransactionType.query, get_label = 'type', validators = [DataRequired('Item Obrigatório')])
    topic = QuerySelectMultipleField('Topicos', allow_blank=False, query_factory= lambda : Topic.query.filter(Topic.selectable == True), get_label = 'name', validators = [DataRequired('Item Obrigatório')])
    sub_topics = QuerySelectMultipleField('Sub-Tópicos', allow_blank=True, query_factory= lambda : SubTopic.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    finalyties = QuerySelectMultipleField('Finalidades', allow_blank=False, query_factory= lambda : TransactionFinality.query, get_label='name', validators=[DataRequired('Item Obrigatório')])
    submit = SubmitField('Salvar')
    prints = SubmitField('Opções')


class TransactionOptionForm(FlaskForm):
    transaction = StringField('Transação', render_kw={'disabled':''})
    option = StringField('Opção')
    description = TextAreaField('Descrição', validators=[DataRequired('Item obrigatório'), Length(min=8, max=540, message='A descrição deve ter entre 8 e 540 caracteres')])
    save = SubmitField('Salvar')
    add = SubmitField('Nova Opção')
    

# class OptionForm(FlaskForm):
#     transaction = FieldList(FormField(TransactionOptionForm), min_entries=1)
#     submit = SubmitField('Salvar')   


class TransactionScreenForm(FlaskForm):
    transaction = StringField('Transação', render_kw={'disabled':''})
    transaction_option = SelectField('Opção')
    files = MultipleFileField("Arquivos")
    description = TextAreaField('Descrição', validators=[DataRequired('Item obrigatório'), Length(min=8, max=540, message='A descrição deve ter entre 8 e 540 caracteres')])
    save = SubmitField('Salvar')
    add = SubmitField('Nova Tela')
    


    def __init__(self, formdata=..., **kwargs): #tid, formdata = ..., *args,
        super().__init__(formdata, **kwargs)
        options = [(None, 'Selecione uma opção')]
        if kwargs.get('tid', False) is False:
            raise Exception('Nenhuma transação informada')
        options.extend([(_.id, _.option) for _ in TransactionOption.query.filter(TransactionOption.transaction_id == kwargs.get('tid'))])
        self.transaction_option.choices = options
        # self.transaction_option.process()
        
        
        