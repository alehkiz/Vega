from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, request, g
from flask_security import current_user, login_required
from flask_security.decorators import roles_accepted
from datetime import datetime 
from wtforms.validators import IPAddress

from app.core.db import db
from app.models.security import User
from app.forms.user import UserForm, CreateUserForm
from app.utils.routes import counter

bp = Blueprint('user', __name__, url_prefix='/user/')

@bp.before_request
@counter
def before_request():
    pass

@bp.route('/')
@bp.route('/index/')
def index():
    # TODO: create route
    return render_template('base.html')

@bp.route('/add/', methods=['GET', 'POST'])
def add():
    form = CreateUserForm()
    error = False
    if form.validate_on_submit():
        user = User.query.filter(User.username.ilike(form.username.data.lower())).first()
        if not user is None:
            error = True
            form.username.errors.append("Usuário inválido ou já existente")
        user = User.query.filter(User.email.ilike(form.email.data.lower())).first()
        if not user is None:
            error = True
            form.email.errors.append('Email inválido ou já existente')
        user = User()
        user.username = form.username.data.lower()
        user.name = form.name.data
        user.email = form.email.data.lower()
        user.about_me = form.about_me.data
        user.active = form.active.data
        user.roles.append(form.role.data)
        _ip = request.access_route[0] or request.remote_addr
        if IPAddress.check_ipv4(_ip):
            user.created_ip = _ip
        else:
            form.submit.errors.append('Erro interno')
        user.password = app.config['DEFAULT_PASS']
        if not form.errors:
            try:
                db.session.commit()
                flash('Usuário criado com sucesso', category='success')
                return redirect(url_for('user.view', id=user.id))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                return render_template('add.html', form=form, title='Adicionar', user=True)

    return render_template('add.html', form=form, title='Adicionar', user=True)
@bp.route('/view/<int:id>/')
def view(id):
    # TODO: create route
    user = User.query.filter_by(id=id).first_or_404()

    return render_template('view.html', item=user, user=True)

@bp.route('/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def edit(id):
    user = User.query.filter_by(id=id).first_or_404()
    form = UserForm()
    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.name = form.name.data
            user.email = form.email.data
            user.about_me = form.about_me.data
            user.updated_at = datetime.utcnow()
            user.active = form.active.data
            user.created_ip = request.remote_addr
            db.session.commit()
            flash('Usuário atualizado com sucesso', category='success')
            return redirect(url_for('user.view', id=user.id))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('edit.html', form=form, title='Editar', user=True)
    form.username.data = user.username
    form.name.data = user.name
    form.email.data = user.email
    form.about_me.data = user.about_me
    form.active.data = user.active
    return render_template('edit.html', form=form, title='Editar', user=True)

@bp.route('/remove/<int:id>')
def remove(id):
    user = User.query.filter_by(id=id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return render_template('base.html'  )

