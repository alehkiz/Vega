from app.models.search import Search
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, g, abort, request
from flask_security import login_required, current_user
from datetime import datetime

from app.core.db import db
from app.models.wiki import Article, Question, Tag
from app.forms.question import QuestionSearchForm
from app.forms.search import SearchForm

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
        # g.question_search_form = QuestionSearchForm()
    g.search_form = SearchForm()
    g.tags = Tag.query.all()
    g.questions_most_viewed = Question.most_viewed(app.config.get('ITEMS_PER_PAGE', 5))
    g.questions_most_recent = Question.query.order_by(Question.create_at.desc()).limit(app.config.get('ITEMS_PER_PAGE', 5)).all()


@bp.route('/')
@bp.route('/index')
def index():
    print(current_user.is_anonymous)
    article = Article.query.first()
    return render_template('article.html', article=article)


@bp.route('/search')
def search():
    # print(g.tags)
    page = request.args.get('page', 1, type=int)
    if g.search_form.validate():
        # print('validado')
        search = Search.query.filter(Search.text.ilike(g.search_form.q.data)).first()
        if search is None:
            search = Search()
            search.text = g.search_form.q.data
            db.session.add(search)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return abort(500)
        else:
            search.add_count()
        paginate = Question.search(g.search_form.q.data, page=page, per_page=app.config.get('ITEMS_PER_PAGE'))
    # article = Article.search(g.search_form.q.data, False, resume=True)
    # result = question.union_all(article).paginate(page=page, per_page=app.config.get('ITEMS_PER_PAGE'))
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None
    # result_question = Question.search()
    return render_template('search.html',cls_question=Question, 
                    pagination=paginate, first_page=first_page, last_page=last_page,
                    url_arguments={'q':g.search_form.q.data})