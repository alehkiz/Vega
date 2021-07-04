from logging import error
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, request, g, session as fsession
from flask_security import current_user, login_user, logout_user
from sqlalchemy.orm import session
from werkzeug.urls import url_parse
from datetime import datetime

from app.models.security import User
from app.forms.login import LoginForm
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
        # print(app.config['SECURITY_PASSWORD_SALT'])
        # print(user)
        # print(login.password.data)
        # print(user.check_password(login.password.data))
        if user is None or not user.check_password(login.password.data):
            flash('Senha ou usuário inválido', category='danger')
            return render_template('login.html', form=login, title='Login')#redirect(url_for('auth.login'))
        if not user.is_active:
            flash('Usuário inativo', category='danger'),
            return redirect(url_for('auth.login'))
        if user.is_temp_password:
            flash('É necessário alterar sua senha.', category='message')
            
            fsession['temp_user'] = user.username
            return redirect(url_for('auth.change_password'))
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

@bp.route('/temp_password/')
def change_password():
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
    print(fsession['temp_user'])
    

    return 'True'

@bp.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('main.index'))