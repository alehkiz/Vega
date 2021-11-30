from flask import Blueprint, request, render_template, current_app, abort
from flask_security import login_required, current_user, roles_accepted
from app.core.db import db
from app.forms.upload import UploadForm
from os.path import splitext, join
from os import stat

from app.models.app import FilePDF

bp = Blueprint('upload', __name__, url_prefix='/upload/')

@bp.route('/send', methods=['POST', 'GET'])
@login_required
@roles_accepted('admin')
def index():
    print('aqui')
    print(request.form)
    form = UploadForm()
    print(form.file_upload)
    if form.validate_on_submit():
        print('submit')
        file_uploaded = form.file_upload.data
        print(file_uploaded)
        if file_uploaded != '':
            file_ext = splitext(file_uploaded.filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                form.file_upload.errors.append('Arquivo não aceito, envie apenas arquivos no formato PDF')
                return render_template('upload.html', form=form)
                print('File not accepted')
                abort(400)
            file = FilePDF()
            file.uploaded_user_id = current_user.id
            file.mimetype = file_uploaded.content_type
            file.file_name = file_uploaded.filename
            file.active = True
            file.path = join(current_app.config['UPLOAD_FOLDER'], file_uploaded.filename)
            file.reference_date = form.reference_date.data
            print(form.reference_date.data)
            file_uploaded.save(join(current_app.config['UPLOAD_FOLDER'], file_uploaded.filename))
            size = stat(join(current_app.config['UPLOAD_FOLDER'], file_uploaded.filename)).st_size
            file.size = size
            db.session.add(file)
            db.session.commit()
            return 'sucesso'
    return render_template('upload.html', form=form)

# @bp.route('/index/')
# def index():
#     ...