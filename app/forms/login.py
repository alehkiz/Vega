from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
# from app.utils.kernel import validate_password


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3,max=32, message='Usuário deve ter entre 3 e 32 caracteres')])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6,max=64, message='Senha deve ter entre 6 e 64 caracteres')])
    remember_me = BooleanField('Manter conectado')
    submit = SubmitField('Logar')

    # def validate_password(form, field):
    #     _temp_validate_password = validate_password(field.data)
    #     if not _temp_validate_password['ok']:
    #         if not _temp_validate_password['digit']:
    #             raise ValidationError('A senha deve conter dígito')
    #         if not _temp_validate_password['uppercase']:
    #             raise ValidationError('A senha deve ter uma letra maiúscula')
    #         if not _temp_validate_password['lowercase']:
    #             raise ValidationError('A senha deve ter uma letra minúscula')