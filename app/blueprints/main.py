from app.models.search import Search
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, g, abort, request, current_app as app, Response, make_response, session
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

@bp.before_app_first_request
def before_first_request():
    ...


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
    g.question_search_form = SearchForm()
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        # user = current_user
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error('Não foi possível salvar ultima visualização do usuário')
            app.logger.error(e)
        # g.question_search_form = QuestionSearchForm()
    
    g.tags = Tag.query.all()
    g.topics = Topic.query.all()
    
    if not session.get('AccessType', False):
        # print(request.cookies.get('AccessType', False), 'Aqui')
        # print(session.get('AccessType', False), 'Session')
        current_rule = request.url_rule
        # print(current_rule.endpoint)
        if current_rule.endpoint not in ['main.select_access', 'static']:
            return redirect(url_for('main.select_access'))
    else:
        # print(request.cookies.get('AccessType', False), 'Dois')
        if session.get('AccessType', False) in [_.name for _ in g.topics]:
            g.selected_access = session.get('AccessType', False)
        else:
            resp = make_response(redirect(url_for('question.index')))
            resp.set_cookie(key='AccessType', value='', expires=0)
            flash('Ocorreu um erro', category='danger')
            return resp

    g.questions_most_viewed = Question.most_viewed(app.config.get('ITEMS_PER_PAGE', 5))
    g.questions_most_recent = Question.query.order_by(Question.create_at.desc()).filter(Question.answer_approved==True).limit(app.config.get('ITEMS_PER_PAGE', 5)).all()
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
    return render_template('base.html')

@bp.route('/select_access/')
@bp.route('/select_access/<string:topic>')
def select_access(topic=None):
    if topic is None:
        return render_template('select_access.html')
    obj_topic = Topic.query.filter(Topic.name.ilike(topic.lower())).first_or_404()
    response = make_response(redirect(url_for('question.index')))
    response.set_cookie(key='AccessType', value=obj_topic.name)
    session['AccessType'] = obj_topic.name
    return response
    # print(obj_topic)
    # return topic
    # if request.cookies.get('AccessType', False):
    #     flash('Módulo selecionado')
    #     return redirect(url_for('question.index'))
    # response = Response()
    # response.set_cookie(key='AccessType', value='ValuePage')

    

@bp.route('/access/<string:topic>')
def selected_access(topic=None):
    if topic is None:
        return redirect(url_for('main.select_access'))

    obj_topic = Topic.query.filter(Topic.name.ilike(topic.lower())).first_or_404()
    response = make_response(redirect(url_for('main.index')))
    response.set_cookie(key='AccessType', value=obj_topic.name)
    return response

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

