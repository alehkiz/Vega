from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, request, g
from flask_security import current_user, login_required
from flask_security.decorators import roles_accepted
from datetime import datetime 

from app.core.db import db
from app.models.security import User
from app.forms.user import UserForm

bp = Blueprint('user', __name__, url_prefix='/user/')

@bp.route('/')
@bp.route('/index/')
def index():
    # TODO: create route
    return render_template('base.html')

@bp.route('/add/')
def add():
    # TODO: create route
    return render_template('base.html')
@bp.route('/view/<int:id>/')
def view(id):
    # TODO: create route
    return render_template('base.html')

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
            user.email = form.name.data
            user.about_me = form.about_me.data
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('user.view', id=user.id))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return render_template('edit.html', form=form, title='Editar', user=True)
    form.username.data = user.username
    form.name.data = user.name
    form.email.data = user.email
    form.about_me.data = user.about_me
    return render_template('edit.html', form=form, title='Editar', user=True)

@bp.route('/remove/<int:id>')
def remove(id):
    # TODO: create route
    return render_template('base.html'  )