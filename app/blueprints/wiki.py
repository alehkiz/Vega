from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort
from flask_security import login_required, current_user

from app.models.wiki import Article

bp = Blueprint('wiki', __name__, url_prefix='/wiki/')

@bp.route('/')
@bp.route('/index')
@bp.route('/<article_id>')
def wiki(article_id=None):
    if article_id is None:
        #TODO em caso do artumento article_id é vazio, retornar todos os artigos
        return abort(404)
    print(type(article_id))
    if not str(article_id).isnumeric():
        return abort(404)
    article = Article.query.filter_by(id=int(article_id)).first_or_404()
    print(article)
    return render_template('article.html', article=article)