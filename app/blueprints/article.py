from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort
from flask_security import login_required, current_user
from flask_security.decorators import roles_accepted
from app.core.db import db
from app.models.wiki import Article, Tag, Topic
from app.forms.wiki import ArticleForm
from datetime import datetime

bp = Blueprint('article', __name__, url_prefix='/article/')





@bp.route('/view/<int:id>')
def view(id=None):
    if id is None:
        #TODO em caso do artumento id é vazio, retornar todos os artigos
        return abort(404)
    if not str(id).isnumeric():
        return abort(404)
    try:
        article = Article.query.filter_by(id=int(id)).first_or_404()
    except Exception as e:
        db.session.rollback()
        app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
        app.logger.error(e)
        return abort(500)
    user_id = current_user.id if current_user.is_authenticated else None
    article.add_view(user_id)
    return render_template('article.html', article=article)

@bp.route('/add/')
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def add():
    
    return render_template('base.html')

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def edit(id):
    article = Article.query.filter_by(id=id).first_or_404()
    form = ArticleForm()
    if form.validate_on_submit():
        try:
            print('aqio')
            article.title = form.title.data
            article.description = form.description.data
            article.text = form.text.data
            article.updated_timestamp = datetime.utcnow()
            article.updated_user_id = current_user.id
            db.session.commit()
            return redirect(url_for('article.view', id=article.id))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return render_template('edit.html', form=form, title='Editar', article=True)
    form.title.data = article.title
    form.description.data = article.description
    form.text.data = article.text
    return render_template('edit.html', form=form, title='Editar', article=True)
@bp.route('/remove/<int:id>')
def remove(id):
    
    return render_template('article.html')