from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class ResetPassword(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3,max=32, message='Usuário deve ter entre 3 e 32 caracteres')])
    old_password = PasswordField('Senha atual', validators=[DataRequired(), Length(min=6,max=64, message='Senha deve ter entre 6 e 64 caracteres')])
    
    new_password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6,max=64, message='Senha deve ter entre 6 e 64 caracteres')])
    confirm_new_password = PasswordField('Confirme nova senha', validators=[DataRequired(), Length(min=6,max=64, message='Senha deve ter entre 6 e 64 caracteres')])
    submit = SubmitField('Logar')