from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_wtf.html5 import DateField
from wtforms import SubmitField, TextField, BooleanField, StringField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from app.models.app import FilePDFType
from app.models.wiki import Topic

class SendFileForm(FlaskForm):
    file = FileField('Arquivo', _name='file', validators=[DataRequired('Item Obrigatório')])
    reference_date = DateField('Data', validators=[DataRequired('Item Obrigatório')])
    title = TextField("Titulo", validators=[DataRequired('Item Obrigatório')])
    type = QuerySelectField("Tipo", allow_blank=False, query_factory=lambda: FilePDFType.query.filter(FilePDFType.active == True), get_label='name', validators=[DataRequired('Item Obrigatório')])
    topic = QuerySelectMultipleField('Topic', allow_blank=False, query_factory= lambda: Topic.query.filter(Topic.active == True, Topic.selectable == True), get_label='name', validators=[DataRequired('Item Obrigatório')])
    submit = SubmitField('Enviar')

class EditFileForm(FlaskForm):
    file = FileField("Arquivo", _name='file')
    # file = StringField("Arquivo",render_kw={'disabled':''})
    reference_date = DateField('Data', validators=[DataRequired('Item Obrigatório')])
    title = TextField("Titulo", validators=[DataRequired('Item Obrigatório')])
    type = QuerySelectField("Tipo", allow_blank=False, query_factory=lambda: FilePDFType.query.filter(FilePDFType.active == True), get_label='name', validators=[DataRequired('Item Obrigatório')])
    topic = QuerySelectMultipleField('Topic', allow_blank=False, query_factory= lambda: Topic.query.filter(Topic.active == True, Topic.selectable == True), get_label='name', validators=[DataRequired('Item Obrigatório')])
    approved = BooleanField('Aprovado?')
    active = BooleanField('Ativo')
    file_update = BooleanField('Atualizar arquivo?')
    submit = SubmitField('Enviar') 
