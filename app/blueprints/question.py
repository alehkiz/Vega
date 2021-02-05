from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request
from flask_security import login_required, current_user
from flask_security import roles_accepted
from app.core.db import db
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView


from app.forms.question import QuestionForm

bp = Blueprint('question', __name__, url_prefix='/question/')

@bp.route('/')
@bp.route('/index')
def index():
    print(request.access_route[0])
    question = Question.query.order_by(Question.create_at.desc()).all()
    return render_template('wiki.html', questions=questions, cls_question=Question)

@bp.route('/view')
def view():
    return 'value'

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