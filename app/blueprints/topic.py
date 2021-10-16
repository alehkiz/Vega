from datetime import datetime
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request, escape, g, jsonify
from flask.globals import current_app
from flask_security import login_required, current_user
from flask_security import roles_accepted
from app.core.db import db
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView, Topic
from app.forms.topic import TopicEditForm
from app.forms.question import QuestionSearchForm
from app.utils.routes import counter

bp = Blueprint('topic', __name__, url_prefix='/topic/')




@bp.route('/')
@bp.route('/index')
def index():
    return ''

@bp.route('edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    topic = Topic.query.filter(Topic.id == id).first_or_404()
    form = TopicEditForm()
    if form.validate_on_submit():
        try:
            topic.name = form.name.data
            # question.answer = form.answer.data
            # question.topics = form.topic.data
            # question.topic = form.topic.data
            # question.updater = current_user
            # question.update_at = datetime.utcnow()
            topic.active = form.active.data
            topic.selectable = form.selectable.data
            db.session.commit()
            return redirect(url_for('admin.topic'))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('edit.html', form=form, title='Editar', topic=True)
    
    form.name.data = topic.name
    form.active.data = topic.active
    form.selectable.data = topic.selectable
    # form.topic.data = question.topics
    # form.topic.data = question.topic
    # form.answer.data = question.answer


    return render_template('edit.html',form=form, title='Editar', topic=True)

@bp.route('/add/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def add():
    form = TopicEditForm()
    if form.validate_on_submit():
        topic = Question.query.filter(Topic.name.ilike(form.name.data)).first()
        if not topic is None:
            form.name.errors.append('Marcação já existte')
        if not form.errors:
            topic = Topic()
            topic.name = form.name.data
            topic.user_id = current_user.id
            topic.active = form.active.data
            topic.selectable = form.selectable.data
            try:
                db.session.add(topic)
                db.session.commit()
                return redirect(url_for('admin.topic'))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                return render_template('add.html', form=form, title='Incluir Tópico', topic=True)
    return render_template('add.html', form=form, title='Incluir Tópico', topic=True)

@bp.route('/view/<int:id>')
def view(id):
    page = request.args.get('page', 1, type=int)
    search_form = QuestionSearchForm()
    pagination_args = {'id':id}
    topic = Topic.query.filter_by(id=id).first_or_404()
    paginate = topic.questions.paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None
    return render_template('question.html', 
                                pagination=paginate, 
                                cls_question=Topic, 
                                form=search_form, mode='views', 
                                first_page=first_page, 
                                last_page=last_page, 
                                url_arguments=pagination_args)

@bp.route('/remove/<int:id>')
def remove(id):
    return ''