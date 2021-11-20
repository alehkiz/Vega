from datetime import datetime
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request, escape, g, jsonify
from flask.globals import current_app
from flask_security import login_required, current_user
from flask_security import roles_accepted
from app.core.db import db
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView, Tag
from app.forms.tag import TagEditForm
from app.forms.question import QuestionSearchForm
from app.utils.routes import counter

bp = Blueprint('tag', __name__, url_prefix='/tag/')



@bp.route('/')
@bp.route('/index')
def index():
    return ''

@bp.route('edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    tag = Tag.query.filter(Tag.id == id).first_or_404()
    form = TagEditForm()
    if form.validate_on_submit():
        try:
            tag.name = form.name.data
            # question.answer = form.answer.data
            # question.tags = form.tag.data
            # question.topic = form.topic.data
            # question.updater = current_user
            # question.update_at = datetime.now()
            db.session.commit()
            return redirect(url_for('admin.tag'))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('edit.html', form=form, title='Editar', edit=True)
    
    form.name.data = tag.name
    # form.tag.data = question.tags
    # form.topic.data = question.topic
    # form.answer.data = question.answer


    return render_template('edit.html',form=form, title='Editar', edit=True)

@bp.route('/add/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def add():
    form = TagEditForm()
    if form.validate_on_submit():
        tag = Tag.query.filter(Tag.name.ilike(form.name.data)).first()
        if not tag is None:
            form.name.errors.append('Marcação já existte')
        if not form.errors:
            tag = Tag()
            tag.name = form.name.data
            tag.user_id = current_user.id
            try:
                db.session.add(tag)
                db.session.commit()
                return redirect(url_for('admin.tag'))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                return render_template('add.html', form=form, title='Incluir marcação', tag=True)
    return render_template('add.html', form=form, title='Incluir marcação', tag=True)

@bp.route('/view/<int:id>')
def view(id):
    page = request.args.get('page', 1, type=int)
    search_form = QuestionSearchForm()
    pagination_args = {'id':id}
    tag = Tag.query.filter_by(id=id).first_or_404()
    paginate = Question.query.filter(Question.tags.contains(tag), Question.answer_approved == True).paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None
    return render_template('question.html', 
                                pagination=paginate, 
                                cls_question=Tag, 
                                form=search_form, mode='views', 
                                first_page=first_page, 
                                last_page=last_page, 
                                url_arguments=pagination_args)

@bp.route('/remove/<int:id>', methods=['GET', 'POST'])
def remove(id):
    confirm = request.form.get('confirm', False)
    if confirm != 'true':
        return jsonify({
            'status': 'error',
            'message': 'not confirmed'
        }), 404
    tag = Tag.query.filter(Tag.id == id).first()
    if tag is None:
        return jsonify({
            'status': 'error',
            'message': 'tag not found'
        }), 404
    try:
        db.session.delete(tag)
        db.session.commit()
        return jsonify({
            'id': id,
            'status': 'success'
        }),200
    except Exception as e:
        app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
        app.logger.error(e)
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'database error'
        }), 404