from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup
from flask_security import login_required, current_user
from datetime import datetime

from app.core.db import db
from app.models.wiki import Article

bp = Blueprint('main', __name__, url_prefix='/')

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error('Não foi possível')
            app.logger.error(e)

@bp.route('/')
@bp.route('/index')
def index():
    print(current_user.is_anonymous)
    article = Article.query.first()
    return render_template('article.html', article=article)
