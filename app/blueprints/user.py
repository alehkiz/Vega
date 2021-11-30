from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, request, g, abort, jsonify
from flask_security import current_user, login_required
from flask_security.decorators import roles_accepted
from datetime import datetime 
from wtforms.validators import IPAddress

from app.core.db import db
from app.models.security import User
from app.models.app import Network
from app.forms.user import UserForm, CreateUserForm
from app.utils.routes import counter

bp = Blueprint('user', __name__, url_prefix='/user/')





@bp.route('/')
@bp.route('/index/')
@login_required
@roles_accepted('admin')
def index():
    # TODO: create route
    return render_template('base.html')


@bp.route('/add/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin')
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
            network = Network.query.filter(Network.ip == _ip).first()
            if network is None:
                network = Network()
                network.ip = _ip
                network.created_user_id = current_user.id
                db.session.add(network)
                try:
                    db.session.commit()
                except Exception as e:
                    app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                    app.logger.error(e)
                    db.session.rollback()
                    form.submit.errors.append('Não foi possível concluir, a rede não foi adicionada')
            user.created_network_id = network.id
        else:
            form.submit.errors.append('Erro interno, não foi possível identificar seu IP')
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
                form.errors.add('Não foi possível concluir')
                return render_template('add.html', form=form, title='Adicionar', user=True)

    return render_template('add.html', form=form, title='Adicionar', user=True)


@bp.route('/view/<int:id>/')
@login_required
@roles_accepted('admin')
def view(id):
    # TODO: create route
    user = User.query.filter_by(id=id).first_or_404()

    return render_template('view.html', item=user, user=True)


@bp.route('/edit/<int:id>/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin')
def edit(id):
    user = User.query.filter_by(id=id).first_or_404()
    form = UserForm()
    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.name = form.name.data
            user.email = form.email.data
            user.about_me = form.about_me.data
            user.updated_at = datetime.now()
            user.active = form.active.data
            user.created_ip = request.remote_addr
            user.roles = form.role.data
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
    form.role.data = user.roles
    return render_template('edit.html', form=form, title='Editar', user=True)


@bp.route('/remove/<int:id>', methods=['POST'])
@login_required
@roles_accepted('admin')
def remove(id):
    confirm = request.form.get('confirm', False)
    if confirm != 'true':
        abort(404)
    u = User.query.filter(User.id == id).first_or_404()
    id = u.id
    try:
        u.active = False
        db.session.commit()
        return jsonify({'id':id,
                    'status': 'success'})
    except Exception as e:
        app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
        app.logger.error(e)
        db.session.rollback()
        return jsonify({
            'message': 'Não foi possível atualizar'
        }), 404
        return abort(404)


    user = User.query.filter_by(id=id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return render_template('base.html'  )


@bp.route('/profile/')
@login_required
def profile():
    return render_template('profile.html')

@bp.route('/user/settings')
@login_required
def settings():
    return 'not implemented'