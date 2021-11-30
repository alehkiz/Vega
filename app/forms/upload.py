from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.html5 import DateField
from wtforms import SubmitField

class UploadForm(FlaskForm):
    file_upload = FileField('Arquivo', _name='file')
    reference_date = DateField('Data')
    submit = SubmitField('Enviar')