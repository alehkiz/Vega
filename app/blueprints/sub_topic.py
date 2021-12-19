from datetime import datetime
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request, escape, g, jsonify
from flask.globals import current_app
from flask_security import login_required, current_user
from flask_security import roles_accepted
from app.core.db import db
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView, SubTopic
from app.forms.sub_topic import SubTopicEditForm
from app.forms.question import QuestionSearchForm
from app.utils.routes import counter

bp = Blueprint('sub_topic', __name__, url_prefix='/sub_topic/')




@bp.route('/')
@bp.route('/index')
def index():
    return ''

@bp.route('edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    sub_topic = SubTopic.query.filter(SubTopic.id == id).first_or_404()
    form = SubTopicEditForm()
    if form.validate_on_submit():
        try:
            sub_topic.name = form.name.data
            # question.answer = form.answer.data
            # question.sub_topics = form.sub_topic.data
            # question.sub_topic = form.sub_topic.data
            # question.updater = current_user
            # question.update_at = datetime.now()
            db.session.commit()
            return redirect(url_for('admin.sub_topic'))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('edit.html', form=form, title='Editar', edit=True)
    
    form.name.data = sub_topic.name
    # form.sub_topic.data = question.sub_topics
    # form.sub_topic.data = question.sub_topic
    # form.answer.data = question.answer


    return render_template('edit.html',form=form, title='Editar', edit=True)

@bp.route('/add/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def add():
    form = SubTopicEditForm()
    if form.validate_on_submit():
        sub_topic = Question.query.filter(SubTopic.name.ilike(form.name.data)).first()
        if not sub_topic is None:
            form.name.errors.append('Marcação já existe')
        if not form.errors:
            sub_topic = SubTopic()
            sub_topic.name = form.name.data
            sub_topic.user_id = current_user.id
            try:
                db.session.add(sub_topic)
                db.session.commit()
                return redirect(url_for('admin.sub_topic'))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                return render_template('add.html', form=form, title='Incluir Sub-Tópico', sub_topic=True)
    return render_template('add.html', form=form, title='Incluir Sub-Tópico', sub_topic=True)

@bp.route('/view/<int:id>')
def view(id):
    page = request.args.get('page', 1, type=int)
    search_form = QuestionSearchForm()
    pagination_args = {'id':id}
    sub_topic = SubTopic.query.filter_by(id=id).first_or_404()
    paginate = sub_topic.questions.paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None
    return render_template('question.html', 
                                pagination=paginate, 
                                cls_question=SubTopic, 
                                form=search_form, mode='views', 
                                first_page=first_page, 
                                last_page=last_page, 
                                url_arguments=pagination_args)

@bp.route('/deactive/<int:id>')
def deactive(id):
    return ''