from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, request, g
from flask_security import current_user, login_required
from flask_security import roles_accepted
from datetime import datetime

from app.models.wiki import Article, Topic, User, Question, Tag, SubTopic
from app.forms.wiki import ArticleForm
from app.core.db import db
from app.utils.routes import counter

bp = Blueprint('support', __name__, url_prefix='/suporte/')


@bp.route('/')
@bp.route('/index/')
@login_required
@roles_accepted('support', 'admin')
def index():
    support = Topic.query.filter(Topic.name == 'Suporte').first_or_404()
    page = request.args.get('page', 1, type=int)
    questions = Question.query.filter(Question.answer_approved==True, Question.topic_id == support.id).order_by(Question.create_at.desc())
    paginate = questions.paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None
    return render_template('question.html', pagination=paginate, cls_question=Question, mode='views', first_page=first_page, last_page=last_page)
