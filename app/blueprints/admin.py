from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, request, g
from flask_security import current_user, login_required
from datetime import datetime

from app.models.wiki import Article, User
from app.forms.wiki import ArticleForm
from app.core.db import db

bp = Blueprint('admin', __name__, url_prefix='/admin/')

@bp.route('/')
def index():
    return render_template('base.html')

@bp.route('/users/')
def users():
    page = request.args.get('page', 1, type=int)
    paginate = User.query.paginate(page, app.config['ITEMS_PER_PAGE'], False)
    first_page = list(paginate.iter_pages())[0]
    last_page = list(paginate.iter_pages())[-1] if list(paginate.iter_pages())[-1] != first_page else None
    return render_template('admin.html', pagination=paginate, first_page=first_page, last_page=last_page, endpoint='admin.users', cls_table=User)

@bp.route('/articles/')
def articles():
    print(request.blueprint)
    print(request.url_rule.endpoint)
    page = request.args.get('page', 1, type=int)
    paginate = Article.query.paginate(page, app.config['ITEMS_PER_PAGE'], False)
    first_page = list(paginate.iter_pages())[0]
    last_page = list(paginate.iter_pages())[-1] if list(paginate.iter_pages())[-1] != first_page else None
    return render_template('admin.html', pagination=paginate, first_page=first_page, last_page=last_page, endpoint=request.url_rule.endpoint, cls_table=Article, obj_endpoint='')

@bp.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit(article_id):
    article = Article.query.filter_by(id=article_id).first_or_404()
    form = ArticleForm()
    if form.validate_on_submit():
        try:
            article.title = form.title.data
            article.description = form.description.data
            article.text = form.text.data
            article.updated_timestamp = datetime.utcnow()
            article.updated_user_id = current_user.id
            db.session.commit()
            return redirect(url_for('wiki.article', article_id=article.id))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return render_template('edit.html', form=form)
    form.title.data = article.title
    form.description.data = article.description
    form.text.data = article.text
    return render_template('edit.html', form=form, title='Editar')