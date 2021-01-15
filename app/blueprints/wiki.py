from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort
from flask_security import login_required, current_user

from app.models.wiki import Article, Tag, Topic

bp = Blueprint('wiki', __name__, url_prefix='/wiki/')

@bp.route('/index')
def index():
    return 'false'

@bp.route('/<article_id>')
def wiki(article_id=None):
    if article_id is None:
        #TODO em caso do artumento article_id é vazio, retornar todos os artigos
        return abort(404)
    if not str(article_id).isnumeric():
        return abort(404)
    article = Article.query.filter_by(id=int(article_id)).first_or_404()
    return render_template('article.html', article=article)

@bp.route('/tag/<tag_name>')
def tag(tag_name=None):
    if tag_name is None:
        return abort(404)
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    return render_template('tags.html', tag=tag)