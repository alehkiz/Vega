from app.models.search import Search
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, g, abort, request, current_app as app
from flask_security import login_required, current_user
from datetime import datetime

from app.core.db import db
from app.models.wiki import Article, Question, Tag, Topic
from app.models.app import Page, Visit
from app.models.security import User
from app.forms.question import QuestionSearchForm
from app.forms.search import SearchForm
from app.utils.routes import counter

# from app.dashboard import dash
from app.utils.dashboard import Dashboard

bp = Blueprint('main', __name__, url_prefix='/')

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        # user = current_user
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error('Não foi possível')
            app.logger.error(e)
        # g.question_search_form = QuestionSearchForm()
    # else:
    #     user = User.query.filter(User.id == app.config.get('USER_ANON_ID')).first()
    #     if user is None:
    #         app.logger.error('Usuário anonimo não encontrado')
    #         app.logger.error()
    #         abort(500)

    g.search_form = SearchForm()
    g.question_search_form = SearchForm()
    g.tags = Tag.query.all()
    g.topics = Topic.query.all()
    g.questions_most_viewed = Question.most_viewed(app.config.get('ITEMS_PER_PAGE', 5))
    g.questions_most_recent = Question.query.order_by(Question.create_at.desc()).limit(app.config.get('ITEMS_PER_PAGE', 5)).all()
    g.questions_most_liked = Question.most_liked(app.config.get('ITEMS_PER_PAGE', 5), classification=False)
    # if request.endpoint != 'static' and not request.endpoint is None:
    #     print(request.url_rule.rule)
    #     page = Page.query.filter(Page.endpoint == request.endpoint).first()
    #     if page is None:
    #         page = Page()
    #         page.endpoint = request.endpoint
    #         page.route = request.url_rule.rule.split('<')[0]
    #         db.session.add(page)
    #         try:
    #             db.session.commit()
    #             page.add_view(user.id)
    #         except Exception as e:
    #             db.session.rollback()
    #             app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
    #             app.logger.error(e)
    #             return abort(500)
    #     else:
    #         page.add_view(user.id)
        # print(request.endpoint)

@bp.before_request
@counter
def before_request():
    pass

@bp.route('/')
@bp.route('/index')
def index():
    return redirect(url_for('question.index'))
    article = Article.query.first()
    return render_template('article.html', article=article)


@bp.route('/search')
def search():
    # print(g.tags)
    page = request.args.get('page', 1, type=int)
    if g.search_form.validate():
        search = Search.query.filter(Search.text.ilike(g.search_form.q.data)).first()
        if search is None:
            search = Search()
            search.text = g.search_form.q.data
            search.add_search(current_user.id)
            db.session.add(search)
            try:
                db.session.commit()
                if current_user.is_authenticated:
                    search.add_search(current_user.id)
                else:
                    search.add_search()
            except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return abort(500)
        else:
            if current_user.is_authenticated:
                search.add_search(current_user.id)
            else:
                search.add_search()
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

