from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request
from flask_security import login_required, current_user
from app.core.db import db
from app.models.wiki import Article, Tag, Topic

bp = Blueprint('wiki', __name__, url_prefix='/wiki/')

@bp.route('/')
@bp.route('/index')
def index():
    print(request.access_route[0])
    articles = Article.query.order_by(Article.timestamp.desc()).all()
    return render_template('wiki.html', articles=articles, cls_article=Article)

@bp.route('/topic/<string:topic_name>')
def topic(topic_name):
    topic = Topic.query.filter_by(formated_name=topic_name).first_or_404()
    articles = topic.articles.all()
    return render_template('wiki.html', articles=articles, cls_article=Article, title= f'{topic.name}')

@bp.route('/tag/<string:tag_name>')
def tag(tag_name=None):
    if tag_name is None:
        return abort(404)
    tag = Tag.query.filter_by(name=tag_name).first_or_404()
    return render_template('tags.html', tag=tag)