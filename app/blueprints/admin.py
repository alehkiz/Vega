from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, request, g
from flask_security import current_user, login_required
from flask_security import roles_accepted
from datetime import datetime

from app.models.wiki import Article, Topic, User, Question, Tag
from app.forms.wiki import ArticleForm
from app.core.db import db

bp = Blueprint('admin', __name__, url_prefix='/admin/')

@bp.route('/')
@login_required
@roles_accepted('admin')
def index():
    return render_template('base.html')

@bp.route('/users/')
@login_required
@roles_accepted('admin')
def users():
    page = request.args.get('page', 1, type=int)
    paginate = User.query.paginate(page, app.config.get('TABLE_ITEMS_PER_PAGE', 10), False)
    first_page = list(paginate.iter_pages())[0]
    last_page = paginate.pages#list(paginate.iter_pages())[-1]
    return render_template('admin.html', pagination=paginate, first_page=first_page, last_page=last_page, endpoint='admin.users', cls_table=User, list=True, page_name='Usuários')

@bp.route('/articles/')
@login_required
@roles_accepted('admin')
def articles():
    page = request.args.get('page', 1, type=int)
    paginate = Article.query.paginate(page, app.config.get('TABLE_ITEMS_PER_PAGE',10), False)
    first_page = list(paginate.iter_pages())[0]
    last_page = paginate.pages#list(paginate.iter_pages())[-1] if list(paginate.iter_pages())[-1] != first_page else None
    return render_template('admin.html', pagination=paginate, first_page=first_page, 
                        last_page=last_page, endpoint=request.url_rule.endpoint, 
                        cls_table=Article, list=True, page_name='Artigos')

@bp.route('/questions')
@login_required
@roles_accepted('admin')
def questions():
    page = request.args.get('page', 1, type=int)
    paginate = Question.query.paginate(page, app.config.get('TABLE_ITEMS_PER_PAGE', 10), False)
    first_page = list(paginate.iter_pages())[0] if len(list(paginate.iter_pages())) >= 1 else None
    last_page = paginate.pages
    return render_template('admin.html', pagination=paginate, first_page=first_page, 
                        last_page=last_page, endpoint=request.url_rule.endpoint, 
                        cls_table=Question, list=True, page_name='Dúvidas')

@bp.route('/topic')
@login_required
@roles_accepted('admin')
def topic():
    page = request.args.get('page', 1, type=int)
    paginate = Topic.query.paginate(page, app.config.get('TABLE_ITEMS_PER_PAGE', 10), False)
    first_page = list(paginate.iter_pages())[0] if len(list(paginate.iter_pages())) >= 1 else None
    last_page = paginate.pages
    return render_template('admin.html', pagination=paginate, first_page=first_page, 
                        last_page=last_page, endpoint=request.url_rule.endpoint, 
                        cls_table=Topic, list=True, page_name='Dúvidas')

@bp.route('/tag')
@login_required
@roles_accepted('admin')
def tag():
    page = request.args.get('page', 1, type=int)
    paginate = Tag.query.paginate(page, app.config.get('TABLE_ITEMS_PER_PAGE', 10), False)
    first_page = list(paginate.iter_pages())[0] if len(list(paginate.iter_pages())) >= 1 else None
    last_page = paginate.pages
    # print(paginate.items)
    return render_template('admin.html', pagination=paginate, first_page=first_page, 
                        last_page=last_page, endpoint=request.url_rule.endpoint, 
                        cls_table=Tag, list=True, page_name='Tags')