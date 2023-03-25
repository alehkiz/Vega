from datetime import datetime
from flask.json import jsonify
from app.utils.html import process_html
from app.utils.kernel import convert_datetime_to_local
from app.utils.routes import counter
from flask.helpers import flash, url_for
from werkzeug.utils import redirect
from app.models.app import Network
from app.models.notifier import Notifier, NotifierLevel, NotifierPriority, NotifierStatus
from app.forms.notifier import NotifierForm
from flask import Blueprint, render_template, g, request, current_app as app, abort
from app.core.db import db
from flask_security import login_required, roles_accepted, current_user
from app.utils.routes import counter


bp = Blueprint('notifier', __name__, url_prefix='/notificacao')

@bp.route('/')
def index():
    notices_active = db.session.query(Notifier).join(NotifierStatus, Notifier.status).join(NotifierPriority, Notifier.priority).filter(NotifierStatus.status == 'Ativo').order_by(NotifierPriority.order.asc(), Notifier.create_at.desc())
    # Notifier.query.filter(NotifierStatus.status == 'Ativo')
    notices_history = db.session.query(Notifier).join(NotifierStatus, Notifier.status).join(NotifierPriority, Notifier.priority).filter(NotifierStatus.status == 'Histórico').order_by(NotifierPriority.id.asc())
    # Notifier.query.filter(NotifierStatus.status == 'Histórico')
    return render_template('notifier.html', notices_active = notices_active, notices_history = notices_history)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'support')
def add():
    form = NotifierForm()
    error = False
    if form.validate_on_submit():
        nf = Notifier.query.filter(Notifier.title.ilike(form.title.data.lower())).first()
        if not nf is None:
            error = True
            form.title.errors.append('Titulo inválido ou já existente')
            return render_template('add.html', form=form, title='Adicionar', notifier=True)
        nf = Notifier.query.filter(Notifier.content.ilike(form.content.data.lower())).first()
        if not nf is None:
            error = True
            form.content.errors.append('Conteudo inválido ou já existente')
            return render_template('add.html', form=form, title='Adicionar', notifier=True)
        nf = Notifier()
        nf.title = form.title.data
        nf.content = form.content.data
        nf.status = form.status.data
        nf.level = form.level.data
        nf.priority = form.priority.data
        nf.topics.extend(form.topics.data)
        nf.sub_topics.extend(form.sub_topics.data)
        nf.created_user_id = current_user.id
        if form.autoload.data == True:
            temp_nf = Notifier.query.filter(Notifier.sub_topics.contains(*form.sub_topics.data), Notifier.autoload == True).first()
            if not temp_nf is None:
                # status = NotifierStatus.query.filter(NotifierStatus.status == 'Histórico').first()
                # temp_nf.status =status
                temp_nf.autoload = False
        nf.autoload = form.autoload.data
        _ip = Network.query.filter(Network.id == g.ip_id).first()
        if _ip is None:
            _ip = Network()
            _ip.ip = request.access_route[0] or request.remote_addr
            db.session.add(_ip)
            try:
                db.session.commit()
                g.ip_id = _ip.id
            except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get("_ERRORS").get("DB_COMMIT_ERROR"))
                app.logger.error(e)
                return abort(500)
        nf.created_network_id = _ip.id
        if not error:
            try:
                db.session.add(nf)
                db.session.commit()
                flash('Notificação criada com sucesso', category='success')
                return redirect(url_for('admin.notifier'))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                form.errors.add('Não foi possível concluir')
                return render_template('add.html', form=form, title='Adicionar', notifier=True)

    return render_template('add.html', form=form, title='Adicionar', notifier=True)

@bp.route('/view/<int:id>')
@login_required
@roles_accepted('admin', 'support')
@counter
def view(id: int):
    notification = Notifier.query.filter(Notifier.id == id).first_or_404()

    return render_template('notifier.html', notification_dict=notification.to_dict_detail)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'support')
def edit(id: int):
    nf = Notifier.query.filter(Notifier.id == id).first_or_404()
    form = NotifierForm()
    if form.validate_on_submit():
        nf.title = form.title.data
        nf.content = process_html(form.content.data).text
        if form.status.data.status == 'Histórico' and nf.status.status == 'Ativo':
            nf.closed_at = convert_datetime_to_local(datetime.utcnow())
            # nf.level = NotifierLevel.query.filter(NotifierLevel.level_bootstrap == 'info').first()
        if form.status.data.status == 'Ativo' and nf.status.status == 'Histórico':
            nf.closed_at = None
        nf.level = form.level.data
        nf.status = form.status.data
        nf.priority = form.priority.data
        
        nf.topics.extend(form.topics.data)
        nf.sub_topics.extend(form.sub_topics.data)
        nf.updater_user_id = current_user.id
        if nf.autoload != form.autoload.data:
            if form.autoload.data is True:
                temp_nf = Notifier.query.filter(Notifier.sub_topics.contains(*form.sub_topics.data), Notifier.autoload == True).first()
                if not temp_nf is None:
                    # status = NotifierStatus.query.filter(NotifierStatus.status == 'Histórico').first()
                    # temp_nf.status =status
                    temp_nf.autoload = False
        nf.autoload = form.autoload.data
        try:
            db.session.commit()
            flash('Notificação criada com sucesso', category='success')
            return redirect(url_for('notifier.view', id=nf.id))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('edit.html', form=form, title='Editar', notifier=True)
    form.title.data = nf.title
    form.content.data = nf.content
    form.status.data = nf.status
    form.priority.data = nf.priority
    form.topics.data = nf.topics
    form.autoload.data = nf.autoload
    form.sub_topics.data = nf.sub_topics
    form.level.data = nf.level
    return render_template('edit.html', form=form, title='Editar', notifier=True)

@bp.route('/deactive/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'support')
def deactive(id: int):
    confirm = request.form.get('confirm', False)
    if confirm != 'true':
        return jsonify({
            'status': 'error',
            'message': 'not confirmed'
        }), 404
    notifier = Notifier.query.filter(Notifier.id == id).first()
    if notifier is None:
        return jsonify({
            'status': 'error',
            'message': 'notification not found'
        }), 404
    try:
        db.session.delete(notifier)
        db.session.commit()
        return jsonify({
            'id': id,
            'status': 'success'
        }),200
    except Exception as e:
        app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
        app.logger.error(e)
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'database error'
        }), 404
        