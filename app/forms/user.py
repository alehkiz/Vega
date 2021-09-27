from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Email

from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from app.models.security import Role

class UserForm(FlaskForm):
    username = StringField('Usuário',validators=[DataRequired('Item obrigatório'), Length(5, 32, message='username deve ter entre 5 e 32 caracteres')])
    name = StringField('Nome',validators=[DataRequired('Item obrigatório'), Length(5, 128, message='username deve ter entre 5 e 128 caracteres')])
    email = StringField('Email',validators=[DataRequired('Item obrigatório'), Length(5, 128, message='username deve ter entre 5 e 128 caracteres')])
    about_me = TextAreaField('Sobre mim',validators=[DataRequired('Item obrigatório'), Length(5, 512, message='username deve ter entre 5 e 512 caracteres')])
    role = QuerySelectMultipleField("Perfil", allow_blank=False, query_factory= lambda:Role.query, get_label='description', validators=[DataRequired('Item obrigatório')])
    active = BooleanField('Usuário ativo?')
    submit = SubmitField('Enviar')

class CreateUserForm(FlaskForm):
    username = StringField('Usuário',validators=[DataRequired('Item obrigatório'), Length(5, 32, message='username deve ter entre 5 e 32 caracteres')])
    name = StringField('Nome',validators=[DataRequired('Item obrigatório'), Length(5, 128, message='username deve ter entre 5 e 128 caracteres')])
    email = StringField('Email',validators=[DataRequired('Item obrigatório'), Length(5, 128, message='username deve ter entre 5 e 128 caracteres'), Email('Email inválido')])
    about_me = TextAreaField('Sobre mim',validators=[DataRequired('Item obrigatório'), Length(5, 512, message='username deve ter entre 5 e 512 caracteres')])
    active = BooleanField('Usuário ativo?')
    role = QuerySelectField("Perfil", allow_blank=False, query_factory= lambda:Role.query, get_label='description', validators=[DataRequired('Item obrigatório')])
    submit = SubmitField('Enviar')