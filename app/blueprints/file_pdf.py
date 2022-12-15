from flask import Blueprint, current_app as app, render_template, url_for, abort, flash, request, make_response, send_from_directory, g, session
from flask_login.utils import login_required
from flask_security.decorators import roles_accepted
from app.models.app import FilePDF, FilePDFType
from app.models.wiki import Topic
from flask_security import login_required, current_user, roles_accepted
from werkzeug.utils import redirect
from app.core.db import db
from app.forms.file import EditFileForm, SendFileForm
from os.path import splitext, join, isfile, isdir
from os import stat, remove, mkdir, rename

bp = Blueprint('file_pdf', __name__, url_prefix='/files/')


@bp.route('/')
@bp.route('/index')
def index():
    return ''


@bp.route('/<string:file_type>')
def files(file_type):
    file_type_o = FilePDFType.query.filter(FilePDFType.url_route == file_type).first_or_404()

    page = request.args.get("page", 1, type=int)
    topics = Topic.query.filter(Topic.name.ilike(session.get('AccessType'))).all()
    paginate = db.session.query(FilePDF).filter(FilePDF.active == True, FilePDF.approved == True).join(FilePDFType.files).filter(FilePDFType.url_route == file_type).join(FilePDF.topics).filter(Topic.id.in_([_.id for _ in topics])).paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    url_args = dict(request.args)
    url_args['file_type'] = file_type
    url_args.pop('page') if 'page' in url_args.keys() else None
    return render_template('files.html', pagination=paginate, first_page=first_page, last_page=last_page, endpoint=request.url_rule.endpoint, url_args=url_args)

@bp.route('/atas')
def atas():
    page = request.args.get("page", 1, type=int)
    topics = Topic.query.filter(Topic.name.ilike(session.get('AccessType'))).all()
    paginate = db.session.query(FilePDF).filter(FilePDF.active == True, FilePDF.approved == True).join(FilePDFType.files).filter(FilePDFType.name == 'Ata').join(FilePDF.topics).filter(Topic.id.in_([_.id for _ in topics])).paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    # paginate = files.paginate(page, app.config.get( "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    return render_template('files.html', pagination=paginate, first_page=first_page, last_page=last_page, endpoint=request.url_rule.endpoint)

@bp.route('/doc_req')
def doc_req():
    page = request.args.get("page", 1, type=int)
    topics = Topic.query.filter(Topic.name.ilike(session.get('AccessType'))).all()
    paginate = db.session.query(FilePDF).filter(FilePDF.active == True, FilePDF.approved == True).join(FilePDFType.files).filter(FilePDFType.name == 'Documentos e Requerimentos').join(FilePDF.topics).filter(Topic.id.in_([_.id for _ in topics])).paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    # paginate = files.paginate(page, app.config.get( "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    return render_template('files.html', pagination=paginate, first_page=first_page, last_page=last_page, endpoint=request.url_rule.endpoint)

@bp.route('/')
@bp.route('/manuais')
def manuais():
    page = request.args.get("page", 1, type=int)
    topics = Topic.query.filter(Topic.name.ilike(session.get('AccessType'))).all()
    paginate = db.session.query(FilePDF).filter(FilePDF.active == True, FilePDF.approved == True).join(FilePDFType.files).filter(FilePDFType.name == 'Manual').join(FilePDF.topics).filter(Topic.id.in_([_.id for _ in topics])).paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    # paginate = files.paginate(page, app.config.get( "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    return render_template('files.html', pagination=paginate, first_page=first_page, last_page=last_page, endpoint=request.url_rule.endpoint, title_name='Manuais')

@bp.route('/add', methods=['POST', 'GET'])
@login_required
@roles_accepted('admin', 'support')
def add():
    form = SendFileForm()
    if form.validate_on_submit():
        file_uploaded = form.file.data
        if file_uploaded != '':
            if file_uploaded.filename.rsplit('.', 1)[1].lower() not in app.config['UPLOAD_EXTENSIONS']:
                form.file.errors.append(f"Arquivo não aceito, envie apenas arquivos no formato {', '.join(app.config['UPLOAD_EXTENSIONS'])}")
                return render_template('upload.html', form=form)
            
            file = FilePDF()
            file.uploaded_user_id = current_user.id
            file.mimetype = file_uploaded.content_type
            file.file_name = file_uploaded.filename

            if not FilePDF.query.filter(FilePDF.file_name.like(file_uploaded.filename)).first() is None:
                form.file.errors.append('Arquivo já existe')
                return render_template('upload.html', form=form)
            file.active = True
            file.path = join(app.config['UPLOAD_FOLDER'], file_uploaded.filename)
            file.reference_date = form.reference_date.data
            file.title = form.title.data
            file.type = form.type.data
            file.topics.extend(form.topic.data)
            file.approved = True
            if not FilePDF.query.filter(FilePDF.title == file.title).first() is None:
                form.title.errors.append('Arquivo com o mesmo título, já adicionado')
                return render_template('upload.html', form=form)
            # file_path = join(app.config['UPLOAD_FOLDER'], file_uploaded.filename)
            file_uploaded.save(file.path)
            if not isfile(file.path):
                flash('Não foi possível salvar o arquivo', category='warning')
                return render_template('upload.html', form=form)

            size = stat(join(app.config['UPLOAD_FOLDER'], file_uploaded.filename)).st_size
            file.size = size
            try:
                db.session.add(file)
                db.session.commit()
                flash('Arquivo enviado com sucesso', category='success')
                if current_user.is_admin:
                    return redirect(url_for('file_pdf.edit', id=file.id))
                return redirect(url_for('file_pdf.viewer'))
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


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'support')
def edit(id):
    file = FilePDF.query.filter(FilePDF.id == id).first_or_404()
    form = EditFileForm()
    if form.validate_on_submit():
        file_uploaded = form.file.data
        if form.file_update.data is True:
            if file_uploaded != '' and file_uploaded != None:
                if file_uploaded.filename.rsplit('.', 1)[1].lower() not in app.config['UPLOAD_EXTENSIONS']:
                    form.file.errors.append(f"Arquivo não aceito, envie apenas arquivos no formato {', '.join(app.config['UPLOAD_EXTENSIONS'])}")
                    return render_template('upload.html', form=form)
            else:
                form.file.errors.append(f"Nenhum arquivo enviado e o botão 'Atualizar arquivo?' não foi selecionado")
                return render_template('upload.html', form=form)
            old_file_path = join(app.config['OLD_UPLOAD_FOLDER'], file.file_name)
            # new_file_path = join(app.config['UPLOAD_FOLDER'], file.file_name)
            # if file.file_name == file_uploaded.filename:
            file.mimetype = file_uploaded.content_type
            file.path = join(app.config['UPLOAD_FOLDER'], file_uploaded.filename)
            file.file_name = file_uploaded.filename
            if not isdir(app.config['OLD_UPLOAD_FOLDER']):
                mkdir(app.config['OLD_UPLOAD_FOLDER'])
            if isfile(file.path):
                rename(file.path, old_file_path)
            else:
                flash('O arquivo não existe no diretório, foi utilizado o novo arquivo enviado.', category='danger')
            app.logger.info(f"Arquivo {file.path} movido para {old_file_path}")
            file_uploaded.save(file.path)
        file.reference_date = form.reference_date.data
        file.type = form.type.data
        file.title = form.title.data
        file.topics = form.topic.data
        file.update_user_id = current_user.id
        file.approved = form.approved.data
        
        
        if current_user.is_admin:
            if form.approved.data is True:
                file.approved = form.approved.data
                file.active = form.active.data
        
        if not isfile(file.path):
                flash('Não foi possível salvar o arquivo', category='warning')
                return redirect(url_for('file_pdf.edit', id=file.id))
        try:
            db.session.commit()
            flash('Edição salva com sucesso', category='success')
            return redirect(url_for('file_pdf.viewer', id=file.id))
        except Exception as e:
            rename(old_file_path, file.path)
            db.session.rollback()
            app.logger.error(f"Erro ao salvar no banco de dados: {e}")
            return abort(500)
    # form.file.data = file.file_name
    form.reference_date.data = file.reference_date
    form.type.data = file.type
    
            
    form.approved.data = file.approved
    form.active.data = file.active
    form.title.data = file.title
    form.topic.data = file.topics

    return render_template('upload.html', form=form)

@bp.route('/viewer/<int:id>')
def viewer(id=None):
    if not id is None:
        file = FilePDF.query.filter(FilePDF.id == id).first_or_404()
        if current_user.is_authenticated:
            return render_template('view_file.html', file=file)
        else:
            if file.active and file.approved:
                return render_template('view_file.html', file=file)
            else:
                return abort(404)
        return abort(404)
        #FilePDF.active == True, FilePDF.approved == True
        # return render_template('view_file.html', file=file.id)
    else:
        return abort(404)
@bp.route('/view/<int:id>')
def view(id=None):
    if not id is None:
        file = FilePDF.query.filter(FilePDF.id == id).first_or_404()
        if current_user.is_authenticated:
            file.add_view(current_user.id, g.ip_id, g.topic_id)
        else:
            if file.active and file.approved:
                file.add_view(app.config.get('USER_ANON_ID'), g.ip_id, g.topic_id)
            else:
                return abort(404)
        if not isfile(join(app.config['UPLOAD_FOLDER'], file.file_name)):
            return abort(404)
        # binary_pdf = file.path
        response = make_response(send_from_directory(app.config['UPLOAD_FOLDER'], file.file_name))
        if file.mimetype == 'application/pdf':
            response.headers['Content-Type'] = 'application/pdf'
        else:
            response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = \
            f'inline; filename="{file.file_name}";name="{file.file_name}"'
        return response

@bp.route('/deactive/<int:id>')
def deactive(id=None):
    return ''