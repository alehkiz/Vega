from datetime import datetime
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request, escape, g, jsonify
from flask.globals import current_app
from flask_security import login_required, current_user
from flask_security import roles_accepted
from app.core.db import db
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView, Tag
from app.models.security import User
from app.models.search import Search


from app.forms.question import QuestionEditForm, QuestionSearchForm, QuestionForm
bp = Blueprint('question', __name__, url_prefix='/question/')

@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    search_form = QuestionSearchForm()
    paginate = Question.query.order_by(Question.create_at.desc()).paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None
    return render_template('question.html', pagination=paginate, cls_question=Question, form=search_form, mode='views', first_page=first_page, last_page=last_page)


@bp.route('/search/', methods=['GET', 'POST'])
def search():
    page = request.args.get('page', 1, type=int)
    if g.question_search_form.validate():
        paginate = Question.search(g.question_search_form.q.data, per_page = app.config.get('QUESTIONS_PER_PAGE', 1), page = page)#
        search = Search.query.filter(Search.text.ilike(g.question_search_form.q.data)).first()
        if search is None:
            search = Search()
            search.text = g.question_search_form.q.data
            question = Question.query.filter(Question.question.ilike(g.question_search_form.q.data)).first()
            if not question is None:
                search.question_id = question.id
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
        iter_pages = list(paginate.iter_pages())
        first_page =  iter_pages[0] if len(iter_pages) >= 1 else None#url_for('.search',page=iter_pages[0], q= g.question_search_form.q.data)
        last_page = paginate.pages if paginate.pages > 0 else None#url_for('.search',page=iter_pages[-1] if iter_pages[-1] != first_page else None, q= g.question_search_form.q.data)
        
    # if paginate.total == 0:
    #     search = Search.query.filter(Search.text.ilike(g.question_search_form.q.data)).first()
    #     if not search is None:
    #         search.add_count()
    #     else:
    #         search = Search()
    #         search.text = g.question_search_form.q.data
    #         db.session.add(search)
    #         try:
    #             db.session.commit()
    #         except Exception as e:
    #             db.session.rollback()
    #             app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
    #             app.logger.error(e)
    #             return abort(500)
        # form = QuestionForm()
        # if form.validate_on_submit():
        #     try:
        #         question = Question()
        #         question.question = form.question.data
        #         if current_user.is_anonymous:
        #             question.create_user_id = 2
        #         else:
        #             question.create_user_id = current_user.id
        #         db.session.add(question)
        #         db.session.commit()
        #     except Exception as e:
        #         app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
        #         app.logger.error(e)
        #         db.session.rollback()
        #         return render_template('question.html', form=form, question=True, mode='search',cls_question=Question, 
        #                         pagination=paginate, first_page=first_page, last_page=last_page)
        # form.question.data = g.question_search_form.q.data
        # return render_template('question.html', form=form, question=True, mode='search',cls_question=Question, 
        #                         pagination=paginate, first_page=first_page, last_page=last_page)
                
    return render_template('question.html', mode='search',cls_question=Question, 
                    pagination=paginate, first_page=first_page, last_page=last_page,
                    url_arguments={'q':g.question_search_form.q.data})

@bp.route('/view/<int:id>')
def view(id=None):
    question = Question.query.filter(Question.id == id).first_or_404()
    dict_view = {}
    dict_view['id'] = question.id
    dict_view['values'] = {
    'Duvida':question.question,
    'Criado em' : question.format_create_date,
    'answer' : question.answer}
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user = User.query.filter(User.name == 'anon').first()
        if user is None:
            raise Exception('Usuário anônimo não criado')
        user_id = user.id
    question.add_view(user_id)
    return render_template('question.html', mode='view', question=question, cls_question=Question)

@bp.route('edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    question = Question.query.filter(Question.id == id).first_or_404()
    form = QuestionEditForm()
    if form.validate_on_submit():
        try:
            question.question = form.question.data
            question.answer = form.answer.data
            question.tag = form.tag.data
            question.topic = form.topic.data
            question.updater = current_user
            question.update_at = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('question.view', id=question.id))
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('edit.html', form=form, title='Editar', question=True)
    
    form.question.data = question.question
    form.tag.data = question.tag
    form.topic.data = question.topic
    form.answer.data = question.answer


    return render_template('edit.html',form=form, title='Editar', question=True)

@bp.route('remove')
def remove():
    return 'none'

@bp.route('/add/', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'editor', 'aux_editor')
def add():
    form = QuestionEditForm()

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

@bp.route('/tag/<string:name>')
def tag(name):

    tag = Tag.query.filter_by(name=name).first_or_404()
    questions = tag.questions.all()
    return render_template('question.html', questions=questions, cls_question=Question)

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


@bp.route('/like/<int:question_id>', methods=['GET','POST'])
@login_required
def like_action(question_id):
    question = Question.query.filter(Question.id==question_id).first_or_404()
    action = request.form.get('action', False)
    if action is False or action not in ['like', 'unlike']:
        return jsonify({
            'status':'error',
            'message': 'ação inválida'}), 404
    if action == 'like':
        if question.is_liked(current_user.id):
            return jsonify({
                'status':'error',
                'message': 'Usuário já gostou dessa questão'}), 404
        rs = question.add_like(current_user.id)
        if rs is False:
            return jsonify({
                'status':'error',
                'message': 'Usuário já gostou dessa questão'}), 404
        return jsonify({
                'status':'success',
                'message': 'Ação concluída'}), 200
    if action == 'unlike':
        if not question.is_liked(current_user.id):
            return jsonify({
                'status':'error',
                'message': 'Usuário não curtiu essa questão'}), 404
        rs = question.remove_like(current_user.id)
        if rs is False:
            return jsonify({
                'status':'error',
                'message': 'Não foi possível remover o gostar'}), 404
        return jsonify({
                'status':'success',
                'message': 'Ação concluída'}), 200
            



