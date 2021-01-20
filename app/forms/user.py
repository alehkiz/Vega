from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class UserForm(FlaskForm):
    username = StringField('Usuário',validators=[DataRequired('Item obrigatório'), Length(5, 32, message='username deve ter entre 5 e 32 caracteres')])
    name = StringField('Nome',validators=[DataRequired('Item obrigatório'), Length(5, 128, message='username deve ter entre 5 e 128 caracteres')])
    email = StringField('Email',validators=[DataRequired('Item obrigatório'), Length(5, 128, message='username deve ter entre 5 e 128 caracteres')])
    about_me = TextAreaField('Sobre mim',validators=[DataRequired('Item obrigatório'), Length(5, 512, message='username deve ter entre 5 e 512 caracteres')])
    submit = SubmitField('Enviar')