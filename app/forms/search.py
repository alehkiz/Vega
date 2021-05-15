from app.models.wiki import Topic
from operator import sub
from flask.globals import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField

class SearchForm(FlaskForm):
    q = StringField('Busca', validators=[DataRequired('Item Obrigatório'), Length(min=3, max=256, message='Busca limitada entre 3 e 256 caracteres')])
    # filter = SelectField('Filter', choices=[('0', 'Todos'), ('1', 'Habilitação'), ('2', 'Veículos')])
    filter = QuerySelectMultipleField("Filter", query_factory=lambda: Topic.query, get_label='name')
    submit = SubmitField('Buscar', _name='search')
    submit.name = 'search'
    
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)