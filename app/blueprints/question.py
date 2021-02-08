from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request, escape, g
from flask_security import login_required, current_user
from flask_security import roles_accepted
from app.core.db import db
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView


from app.forms.question import QuestionForm, QuestionSearchForm

bp = Blueprint('question', __name__, url_prefix='/question/')

@bp.route('/')
@bp.route('/index')
def index():
    search_form = QuestionSearchForm()
    questions = Question.query.order_by(Question.create_at.desc()).all()
    return render_template('question.html', questions=questions, cls_question=Question, form=search_form)


@bp.route('/search/')
def search():
    
    print(g.question_search_form.validate())
    print(url_for('.search', page=1, q=g.question_search_form.q.data))
    page = request.args.get('page', 1, type=int)
    paginate = Question.search(g.question_search_form.q.data, per_page = app.config.get('ITEMS_PER_PAGE'), page = page)#
    iter_pages = list(paginate.iter_pages())
    first_page =  iter_pages[0] if len(iter_pages) >= 1 else None#url_for('.search',page=iter_pages[0], q= g.question_search_form.q.data)
    last_page = paginate.pages#url_for('.search',page=iter_pages[-1] if iter_pages[-1] != first_page else None, q= g.question_search_form.q.data)
    
    return render_template('question.html', mode='search',cls_question=Question, 
                    pagination=paginate, first_page=first_page, last_page=last_page,
                    url_arguments={'q':g.question_search_form.q.data})


    q = escape(q)
    paginate = Question.search(q)
    return render_template('question.html', mode='search', result=paginate)

@bp.route('/view')
def view(id=None):
    return 'value'

@bp.route('edit')
def edit():
    return 'none'

@bp.route('remove')
def remove():
    return 'none'

@bp.route('/add/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def add():
    form = QuestionForm()

    if form.validate_on_submit():
        question = Question.query.filter(Question.question.ilike(form.question.data)).first()
        if not question is None:
            form.question.errors.append('Título inválido ou já existente')
        if not form.errors:
            question = Question()
            question.question = form.question.data
            question.answer = form.answer.data
            question.create_user_id = current_user.id
            try:
                db.session.add(question)
                db.session.commit()
                return redirect(url_for('question.view', id=question.id))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                return render_template('add.html', form=form, title='Editar', question=True)
    return render_template('add.html', form=form, title='Editar', question=True)


# @bp.route('/topic/<string:topic_name>')
# def topic(topic_name):
#     topic = Topic.query.filter_by(format_name=topic_name).first_or_404()
#     articles = topic.articles.all()
#     return render_template('wiki.html', articles=articles, cls_article=Article, title= f'{topic.name}')

# @bp.route('/tag/<string:tag_name>')
# def tag(tag_name=None):
#     if tag_name is None:
#         return abort(404)
#     tag = Tag.query.filter_by(name=tag_name).first_or_404()
#     return render_template('tags.html', tag=tag)