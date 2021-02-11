from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request
from flask_security import login_required, current_user
from flask_security.decorators import roles_accepted
from app.core.db import db
from app.models.wiki import Article, Tag, Topic
from app.forms.wiki import ArticleForm
from app.utils.kernel import url_in_host
from datetime import datetime

bp = Blueprint('article', __name__, url_prefix='/article/')





@bp.route('/view/<int:id>')
def view(id=None):
    if id is None:
        #TODO em caso do argumento id é vazio, retornar todos os artigos
        return abort(404)
    if not str(id).isnumeric():
        return abort(404)
    # try:
    article = Article.query.filter_by(id=int(id)).first_or_404()
    # except Exception as e:
    #     db.session.rollback()
    #     app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
    #     app.logger.error(e)
    #     return abort(500)
    user_id = current_user.id if current_user.is_authenticated else None
    article.add_view(user_id)
    return render_template('article.html', article=article)

@bp.route('/add/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def add():
    form = ArticleForm()

    if form.validate_on_submit():
        article = Article.query.filter(Article.title.ilike(form.title.data)).first()
        if not article is None:
            form.title.errors.append('Título inválido ou já existente')
        print(form.topic.data)
        if not form.errors:
            article = Article()
            article.title = form.title.data
            article.description = form.description.data
            article.text = form.text.data
            article.user_id = current_user.id
            article.topic_id = form.topic.data.id
            try:
                db.session.add(article)
                db.session.commit()
                return redirect(url_for('article.view', id=article.id))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                return render_template('add.html', form=form, title='Editar', article=True)
    return render_template('add.html', form=form, title='Editar', article=True)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def edit(id):
    article = Article.query.filter_by(id=id).first_or_404()
    form = ArticleForm()
    if form.validate_on_submit():
        try:
            article.title = form.title.data
            article.description = form.description.data
            article.text = form.text.data
            article.update_at = datetime.utcnow()
            article.update_user_id = current_user.id
            db.session.commit()
            return redirect(url_for('article.view', id=article.id))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('edit.html', form=form, title='Editar', article=True)
    form.title.data = article.title
    form.description.data = article.description
    form.text.data = article.text
    return render_template('edit.html', form=form, title='Editar', article=True)
@bp.route('/remove/<int:id>')
def remove(id):
    article = Article.query.filter_by(id=id).first_or_404()
    db.session.delete(article)
    try:
        db.session.commit()
        flash('Artigo removido com sucesso', category='success')
        if request.referrer and url_in_host(request.referrer):
            return redirect(url_for(request.referrer))
        return redirect(url_for('wiki.index'))
    except Exception as e:
        app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
        app.logger.error(e)
        db.session.rollback()
        flash('Ocorreu um erro na exclusão', category='danger')
        if request.referrer and url_in_host(request.referrer):
            return redirect(request.referrer)
        return redirect(url_for('wiki.index'))
    return render_template('article.html')