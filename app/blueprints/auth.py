from logging import error
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, request, g, session as fsession
from flask_login.utils import login_required
from flask_security import current_user, login_user, logout_user
from sqlalchemy.orm import session
from werkzeug.urls import url_parse
from datetime import datetime

from app.models.security import User
from app.forms.login import LoginForm
from app.forms.reset_password import ResetPassword
from app.utils.routes import counter
from app.core.db import db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_request
@counter
def before_request():
    pass

@bp.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    login = LoginForm()
    if login.validate_on_submit():
        user = User.query.filter_by(username=login.username.data).first()
        if user is None or not user.check_password(login.password.data):
            flash('Senha ou usuário inválido', category='danger')
            return render_template('login.html', form=login, title='Login')#redirect(url_for('auth.login'))
        if not user.is_active:
            flash('Usuário inativo', category='danger'),
            return redirect(url_for('auth.login'))
        if user.is_temp_password:
            flash('É necessário alterar sua senha.', category='info')
            
            fsession['temp_user'] = user.username
            return redirect(url_for('auth.temp_password'))
        login_user(user, remember=login.remember_me.data)
        user.last_login_ip = request.remote_addr
        user.last_login_at = datetime.utcnow()
        user.current_login_at = datetime.utcnow()
        user.current_login_ip = request.remote_addr
        user.login_count += 1
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            logout_user()
            return redirect(url_for('auth.login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', form=login, title='Login')

@bp.route('/temp_password/', methods=['GET', 'POST'])
def temp_password():
    if current_user.is_authenticated:
        flash(message='Usuário logado', category='danger')
        return redirect(url_for('auth.login'))
    username = fsession.get('temp_user', False)
    if username is False:
        message = 'Nenhum usuário encontrado'
        flash(message=message, category='danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter(User.username == username).first()
    if user is None:
        message = 'Nenhum usuário encontrado'
        flash(message=message, category='danger')
        return redirect(url_for('auth.login'))
    if not user.is_temp_password:
        message = 'Usuário não tem senha provisória'
        flash(message=message, category='danger')
        return redirect(url_for('auth.login'))
    
    form = ResetPassword()
    form.username.data = user.username
    if form.validate_on_submit():
        if form.new_password.data == form.confirm_new_password.data:
            if not user.check_password(form.old_password.data):
                # senha antiga não é igual a senha do usuário
                message = 'Senha atual incorreta'
                flash(message=message, category='danger')
                return redirect(url_for('auth.login'))
            user.password = form.new_password.data
            user.temp_password = False
            try:
                db.session.commit()
                flash(message='Senha alterada com sucesso, acesse novamente', category='info')
                return redirect(url_for('auth.login'))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return redirect(url_for('auth.login'))
        else:
            form.confirm_new_password.errors.append('Senha não confere com a senha informada.')
            return render_template('reset_password.html', form=form)
    return render_template('reset_password.html', form=form)

@bp.route('/change_password/', methods=['GET', 'POST'])
@login_required
def change_password():
    
    if not current_user.is_authenticated:
        flash(message='Usuário não logado', category='danger')
        return redirect(url_for('main.index'))
    
    form = ResetPassword()
    form.username.data = current_user.username
    if form.validate_on_submit():
        if form.new_password.data == form.confirm_new_password.data:
            if not current_user.check_password(form.old_password.data):
                # senha antiga não é igual a senha do usuário
                message = 'Senha atual incorreta'
                flash(message=message, category='danger')
                return redirect(url_for('auth.login'))
            current_user.password = form.new_password.data
            current_user.temp_password = False
            try:
                db.session.commit()
                flash(message='Senha alterada com sucesso, acesse novamente', category='info')
                return redirect(url_for('auth.login'))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return redirect(url_for('auth.login'))
        else:
            form.confirm_new_password.errors.append('Senha não confere com a senha informada.')
            return render_template('reset_password.html', form=form)
    return render_template('reset_password.html', form=form)

@bp.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('main.index'))