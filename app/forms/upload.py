from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.html5 import DateField
from wtforms import SubmitField, TextField
from wtforms.validators import DataRequired, Length

class UploadForm(FlaskForm):
    file_upload = FileField('Arquivo', _name='file', validators=[DataRequired('Item Obrigatório')])
    reference_date = DateField('Data', validators=[DataRequired('Item Obrigatório')])
    title = TextField("Titulo", validators=[DataRequired('Item Obrigatório')])
    submit = SubmitField('Enviar')