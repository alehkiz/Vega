from flask import Blueprint, current_app as app, render_template, url_for, abort, flash, request, make_response, send_from_directory, g, session
from flask_login.utils import login_required
from flask_security.decorators import roles_accepted
from app.models.app import FilePDF, FilePDFType
from app.models.wiki import Topic
from flask_security import login_required, current_user, roles_accepted
from werkzeug.utils import redirect
from app.core.db import db
from app.forms.file_pdf_type import FilePDFTypeEditForm

from app.models.app import FilePDFType
from os.path import splitext, join, isfile
from os import stat, remove


bp = Blueprint('file_pdf_type', __name__, url_prefix='/file_pdf_type/')


@bp.route('add', methods=['GET', 'POST'])
@roles_accepted('admin')
def add():
    form = FilePDFTypeEditForm()
    if form.validate_on_submit():
        file_type = FilePDFType.query.filter(FilePDFType.name.ilike(form.name.data)).first()
        if not file_type is None:
            form.name.errors.append('Tipo já existe')
        if not form.errors:
            file_type = FilePDFType()
            file_type.name = form.name.data
            file_type.user_id = current_user.id
            try:
                db.session.add(file_type)
                db.session.commit()
                return redirect(url_for('admin.file_pdf_type'))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                return render_template('add.html', form=form, title='Incluir Tipo de Arquivo', file_pdf_type=True)
    return render_template('add.html', form=form, title='Incluir Tipo de Arquivo', file_pdf_type=True)

@bp.route('edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    file_type = FilePDFType.query.filter(FilePDFType.id == id).first_or_404()
    form = FilePDFTypeEditForm()
    if form.validate_on_submit():
        try:
            file_type.name = form.name.data
            file_type.active = form.active.data
            file_type.url_route = form.url_route.data
            db.session.commit()
            return redirect(url_for('admin.file_pdf_type'))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('edit.html', form=form, title='Editar', edit=True)
    
    form.name.data = file_type.name
    form.active.data = file_type.active
    form.url_route.data = file_type.url_route

    return render_template('edit.html',form=form, title='Editar', edit=True)

@bp.route('/deactive/<int:id>')
def deactive(id):
    return ''

@bp.route('/view/<int:id>')
def view(id):
    return ''