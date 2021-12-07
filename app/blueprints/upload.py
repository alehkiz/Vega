from flask import Blueprint, request, render_template, current_app as app, abort, flash, redirect, url_for
from flask_security import login_required, current_user, roles_accepted
from werkzeug.utils import redirect
from app.core.db import db
from app.forms.upload import UploadForm
from os.path import splitext, join, isfile
from os import stat, remove

from app.models.app import FilePDF

bp = Blueprint('upload', __name__, url_prefix='/upload/')


@bp.route('/')
@bp.route('/index')
def index():
    files = FilePDF.query.filter(FilePDF.active == True, FilePDF.approved == True)

    

@bp.route('/send', methods=['POST', 'GET'])
@login_required
@roles_accepted('admin')
def send():
    form = UploadForm()
    if form.validate_on_submit():
        file_uploaded = form.file_upload.data
        if file_uploaded != '':
            # file_ext = splitext(file_uploaded.filename)[1].lower()
            # print(file_ext)
            if file_uploaded.filename.rsplit('.', 1)[1].lower() not in app.config['UPLOAD_EXTENSIONS']:
                form.file_upload.errors.append('Arquivo não aceito, envie apenas arquivos no formato PDF')
                return render_template('upload.html', form=form)
            
            file = FilePDF()
            file.uploaded_user_id = current_user.id
            file.mimetype = file_uploaded.content_type
            file.file_name = file_uploaded.filename

            if not FilePDF.query.filter(FilePDF.file_name.like(file_uploaded.filename)).first() is None:
                form.file_upload.errors.append('Arquivo já existe')
                return render_template('upload.html', form=form)
            file.active = True
            file.path = join(app.config['UPLOAD_FOLDER'], file_uploaded.filename)
            file.reference_date = form.reference_date.data
            file.title = form.title.data
            
            
            if not FilePDF.query.filter(FilePDF.title == file.title).first() is None:
                form.title.errors.append('Arquivo com o mesmo título, já adicionado')
                return render_template('upload.html', form=form)
            # file_path = join(app.config['UPLOAD_FOLDER'], file_uploaded.filename)
            file_uploaded.save(file.path)
            # print(f'Arquivo {file_path} não existe')
            if not isfile(file.path):
                flash('Não foi possível salvar o arquivo', category='warning')
                return render_template('upload.html', form=form)

            size = stat(join(app.config['UPLOAD_FOLDER'], file_uploaded.filename)).st_size
            file.size = size
            try:
                db.session.add(file)
                db.session.commit()
                flash('Arquivo enviado com sucesso', category='success')
                return redirect(url_for('upload.send'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Erro ao salvar no banco de dados: {e}")
                try:
                    if isfile(file.path):
                        remove(file.path)
                        flash(f'Arquivo {file.path} não existe {e}')
                        app.logger.error(f"Arquivo {file.path} não existe")
                        app.logger.error(e)
                        return abort(500)
                except Exception as e:
                    app.logger.error(f"Arquivo {file.path} não existe")
                    app.logger.error(e)
                    return abort(500)
                
            return render_template('upload.html', form=form)
    return render_template('upload.html', form=form)

# @bp.route('/index/')
# def index():
#     ...