from datetime import datetime
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request, escape, g, jsonify, session
from flask.globals import current_app
from flask_security import login_required, current_user, roles_accepted
from app.blueprints.admin import sub_topic
from app.core.db import db
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView, SubTopic, Tag, Topic
from app.models.security import User
from app.models.app import Network
from app.models.search import Search
from app.utils.sql import unaccent
from app.utils.kernel import convert_datetime_to_local, strip_accents
from app.utils.html import process_html
from app.forms.question import QuestionAnswerForm, CreateQuestion, QuestionApproveForm, QuestionEditAndApproveForm
from app.utils.routes import counter
from sqlalchemy import desc, nullslast



from app.forms.question import QuestionEditForm, QuestionSearchForm, QuestionForm
bp = Blueprint('question', __name__, url_prefix='/duvidas/')

@bp.route('/')
@bp.route('/index')
@counter
def index():
    page = request.args.get('page', 1, type=int)
    if not session.get('AccessType', False):
        return redirect(url_for('main.index'))
    sub_topic = request.args.get('sub_topic', False)
    if not sub_topic is False:
        sub_topic = SubTopic.query.filter(SubTopic.name == sub_topic).first()
        if sub_topic is None:
            return abort(404)
    topics = Topic.query.filter(Topic.name.ilike(session.get('AccessType'))).all()
    search_form = QuestionSearchForm()
    if current_user.is_authenticated and current_user.is_support:
        query = db.session.query(Question).filter(Question.answer_approved == True, Question.active == True).order_by(Question.create_at.desc())
    else:
        query = db.session.query(Question).filter(Question.answer_approved == True, Question.active == True).join(Question.topics).filter(Topic.id.in_([_.id for _ in topics])).order_by(Question.create_at.desc())
    # query = Question.query.filter(Question.answer_approved==True, Question.topic_id.in_([_.id for _ in topics])).order_by(Question.create_at.desc())
    if not sub_topic is False:
        paginate = query.filter(Question.sub_topic_id == sub_topic.id).paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    else:
        paginate = query.paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None

    url_args = dict(request.args)
    url_args.pop('page') if 'page' in url_args.keys() else None

    return render_template(
        'question.html', 
        pagination=paginate, 
        cls_question=Question, 
        form=search_form, 
        mode='views', 
        first_page=first_page, 
        last_page=last_page, 
        sub_topics=SubTopic.query,
        url_args=url_args
        )


@bp.route('/search/', methods=['GET', 'POST'])
@counter
def search():
    page = request.args.get('page', 1, type=int)
    search_query = False
    
    if g.question_search_form.validate():
        if not session.get('AccessType', False):
            return redirect(url_for('main.index'))
        topics = Topic.query.filter(Topic.name.ilike(session.get('AccessType'))).all()
        sub_topics = g.question_search_form.filter.data
        if not sub_topics:
            sub_topics = SubTopic.query.all()
        if current_user.is_authenticated and current_user.is_support:
            topics = []
        q = Question.search(g.question_search_form.q.data, pagination=False, sub_topics=sub_topics, topics=topics).filter(Question.answer_approved==True).order_by(desc('similarity'))#.join(QuestionView.question, full=True).filter(Question.answer_approved==True).order_by(QuestionView.count_view.desc())
        
        paginate = q.paginate(per_page = app.config.get('QUESTIONS_PER_PAGE', 1), page = page)
        search_query = strip_accents(g.question_search_form.q.data)
        search = Search.query.filter(unaccent(Search.text).ilike(search_query)).first()
        if search is None:
            search = Search()
            search.text = strip_accents(g.question_search_form.q.data).lower()
            # question = Question.query.filter(Question.question.ilike(g.question_search_form.q.data)).first()
            # if not question is None:
            #     search.question_id = question.id
            db.session.add(search)
            try:
                db.session.commit()
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
            # search.add_count()
        iter_pages = list(paginate.iter_pages())
        first_page =  iter_pages[0] if len(iter_pages) >= 1 else None#url_for('.search',page=iter_pages[0], q= g.question_search_form.q.data)
        last_page = paginate.pages if paginate.pages > 0 else None#url_for('.search',page=iter_pages[-1] if iter_pages[-1] != first_page else None, q= g.question_search_form.q.data)
        if paginate.total == 0:
            form = CreateQuestion()
            topic = Topic.query.filter(Topic.name.ilike(session.get('AccessType'))).first()
            if topic is None:
                return abort(505)
            if form.validate_on_submit():
                question = Question.query.filter(Question.question.ilike(form.question.data)).first()
                if not question is None:
                    form.question.errors.append('Dúvida já cadastrada')
                if not form.errors:
                    if current_user.is_authenticated:
                        user = current_user
                    else:
                        user = User.query.filter(User.id == app.config.get('USER_ANON_ID', False)).first()

                    question = Question()
                    question.question = form.question.data
                    question.topics.append(topic)
                    question.sub_topic = form.sub_topic.data
                    question.create_user_id = user.id
                    question.question_network_id = g.ip_id
                    question.active = False
                    db.session.add(question)
                    try:
                        db.session.commit()
                        flash('Dúvida cadastrada com sucesso!', category='success')
                        return redirect(url_for('question.index'))
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                        app.logger.error(e)
                        return abort(500)
            if search_query is not False:
                form.question.data = strip_accents(g.question_search_form.q.data)
        else:
            form = False

                    
        return render_template('question.html', mode='search',cls_question=Question, 
                        pagination=paginate, first_page=first_page, last_page=last_page, form=form,
                        url_arguments={'q':g.question_search_form.q.data})
    return render_template('question.html', mode='search',cls_question=Question, 
                        form=False,
                        url_arguments={'q':g.question_search_form.q.data})
@bp.route('/view/<int:id>')
@counter
def view(id=None):
    if current_user.is_anonymous:
        question = db.session.query(Question
        ).filter(Question.id == id
        ).join(Question.topics
        ).filter(Topic.id == g.topic.id, Question.active == True
        ).first_or_404()
    else:
        question = Question.query.filter(Question.id == id).first_or_404()
    
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        if not question.was_answered or not question.was_approved:
            return redirect(url_for('question.index'))
        user = User.query.filter(User.name == 'ANON').first()
        if user is None:
            raise Exception('Usuário anônimo não criado')
        user_id = user.id
    question.add_view(user_id, g.ip_id)
    return render_template('question.html', mode='view', question=question, cls_question=Question)

@bp.route('edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted("admin", "support", "manager_content")
def edit(id):
    question = Question.query.filter(Question.id == id).first_or_404()
    if current_user.is_admin:
        form = QuestionEditAndApproveForm()
    else:
        form = QuestionEditForm()
    if form.validate_on_submit():
        # try:
        question.question = process_html(form.question.data).text
        question.tags = form.tag.data
        question.topics = form.topic.data
        question.sub_topic = form.sub_topic.data
        question.update_user_id = current_user.id
        question.update_at = convert_datetime_to_local(datetime.now())
        # question.answer_user_id = current_user.id
        question.answer = process_html(form.answer.data).text

        if current_user.is_admin:
            question.answer_approved = form.approved.data
        if not g.ip_id:
            app.logger('Erro ao salvar o ip ´g.ip_id´ não está definido')
            flash('Não foi possível concluir o pedido')
        question.question_network_id = g.ip_id
        db.session.commit()
        return redirect(url_for('question.view', id=question.id))

    form.question.data = question.question
    form.tag.data = question.tags
    form.topic.data = question.topics
    form.answer.data = question.answer
    form.sub_topic.data = question.sub_topics
    if current_user.is_admin:
        form.approved.data = question.answer_approved
    return render_template('edit.html',form=form, title='Editar', question=True)

@bp.route('activate/<int:id>', methods=['POST'])
@login_required
@roles_accepted('admin', 'support')
def activate(id):
    confirm = request.form.get('confirm', False)
    if confirm != 'true':
        return jsonify({
            'status': 'error',
            'message': 'not confirmed'
        }), 404
    q = Question.query.filter(Question.id == id).first_or_404()
    id = q.id 
    try:
        q.active = True
        db.session.commit()
        return jsonify({'id': id,
                        'status': 'success'})
    except Exception as e:
        app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
        app.logger.error(e)
        db.session.rollback()
        return abort(404)

@bp.route('deactive/<int:id>', methods=['POST'])
@login_required
@roles_accepted("admin", "manager_content", 'support')
@counter
def deactive(id):
    confirm = request.form.get('confirm', False)
    if confirm != 'true':
        return jsonify({
            'status': 'error',
            'message': 'not confirmed'
        }), 404
    q = Question.query.filter(Question.id == id).first()
    if q is None:
        return jsonify({
            'status': 'error',
            'message': 'not found'
        }), 404
    id = q.id 
    try:
        q.active = False
        db.session.commit()
        return jsonify({'id':id,
                    'status': 'success'})
    except Exception as e:
        app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
        app.logger.error(e)
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'database error'
        }), 500
    # return jsonify(q.to_dict())
    return jsonify({'status': 'error'})

@bp.route('active/<int:id>', methods=['POST'])
@login_required
@roles_accepted("admin", "manager_content", 'support')
@counter
def active(id):
    confirm = request.form.get('confirm', False)
    if confirm != 'true':
        return jsonify({
            'status': 'error',
            'message': 'not confirmed'
        }), 404
    q = Question.query.filter(Question.id == id).first()
    if q is None: 
        return jsonify({
            'status': 'error',
            'message': 'not found'
        }), 404
    q.active = True
    try:
        q.active = True
        db.session.commit()
        return jsonify({'id':q.id,
                    'status': 'success'})
    except Exception as e:
        app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
        app.logger.error(e)
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'database error'
        }), 500

@bp.route('/add/', methods=['GET', 'POST'])
@login_required
@roles_accepted("admin", "support", "manager_content")
def add():
    if current_user.is_admin:
        form = QuestionEditAndApproveForm()
    else:
        form = QuestionEditForm()

    if form.validate_on_submit():
        question = Question.query.filter(Question.question.ilike(form.question.data)).first()
        if not question is None:
            form.question.errors.append('Título inválido ou já existente')
        if not form.errors:
            question = Question()
            # remove tags html
            question.question = process_html(form.question.data).text
            
            question.answer_user_id = current_user.id
            
            # remove tag html
            question.answer = process_html(form.answer.data).text
            if not g.ip_id:
                app.logger('Erro ao salvar o ip ´g.ip_id´ não está definido')
                flash('Não foi possível concluir o pedido')
            question.answer_network_id = g.ip_id
            if not g.ip_id:
                app.logger('Erro ao salvar o ip ´g.ip_id´ não está definido')
                flash('Não foi possível concluir o pedido')
            question.question_network_id = g.ip_id
            question.create_user_id = current_user.id
            question.topics.extend(form.topic.data)
            question.sub_topic_id = form.sub_topic.data.id
            question.tags = form.tag.data
            question.active = True
            question.create_at = convert_datetime_to_local(datetime.utcnow())
            question.answer_at = convert_datetime_to_local(datetime.utcnow())
            if current_user.is_admin:
                if form.approved.data is True:
                    question.answer_approved = form.approved.data
                    question.answer_approved_at = convert_datetime_to_local(datetime.utcnow())
                    question.answer_approve_user_id = current_user.id
            try:
                db.session.add(question)
                db.session.commit()
                return redirect(url_for('question.view', id=question.id))
            except Exception as e:
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                return render_template('add.html', form=form, title='Incluir dúvida', question=True)
        else:
            app.logger.error('Form error')
    else:
        app.logger.error('Form not validated.')
    return render_template('add.html', form=form, title='Incluir dúvida', question=True)

@bp.route('/responder/<int:id>', methods=['POST', 'GET'])
@login_required
@roles_accepted("admin", "support", "manager_content")
def answer(id: int):
    q = Question.query.filter(Question.id == id).first_or_404()
    if q.was_answered:
        flash('Questão já foi respondida', category='danger')
        return redirect(url_for('question.index'))
    form = QuestionAnswerForm()
    if form.validate_on_submit():
        if not q is None:
            if q.id != id:
                form.question.errors.append('Você alterou a pergunta para uma já cadastrada')
                return render_template('answer.html', form=form, answer=True)
        q.answer_user_id = current_user.id
        q.answer_network_id = g.ip_id
        q.answer = form.answer.data
        q.answer_at = convert_datetime_to_local(datetime.utcnow())
        q.tags = form.tag.data
        q.topics = form.topic.data
        q.sub_topics = form.sub_topic.data
        q.question = form.question.data
        try:
            db.session.commit()
            return redirect(url_for('question.view', id=q.id))
        except Exception as e:
            form.question.errors.append('Não foi possível atualizar')
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('answer.html', form=form, answer=True)
    
    form.question.data = q.question
    form.topic.data = q.topics
    form.sub_topic.data = q.sub_topics


    return render_template('answer.html', form=form, answer=True)
        # TODO terminar

@bp.route('/aprovar/<int:id>', methods=['POST', 'GET'])
@login_required
@roles_accepted("admin", "manager_content")
def approve(id: int):
    q = Question.query.filter(Question.id == id).first_or_404()
    if not q.was_answered:
        flash('Questão ainda não respondida, responda primeiro para aprovar', category='danger')
        return redirect(url_for('question.answer', id=q.id))
    if q.was_approved:
        flash('Questão já foi aprovada', category='danger')
        return redirect(url_for('admin.to_approve'))
    form = QuestionApproveForm()
    if form.validate_on_submit():
        if not Question.query.filter(Question.question.ilike(form.question.data.lower())).first() is None:
            if q.id != id:
                form.question.errors.append('Você alterou a pergunta para uma já cadastrada')
                return render_template('answer.html', form=form, approve=True)
        if form.repprove.data is True:
            q.answer_approved = False
            flash('Questão reprovada.', category='success')
            return redirect(url_for('question.view', id=q.id))
        # q.answer_user_id = current_user.id
        q.answer_network_id = g.ip_id
        q.answer = form.answer.data
        # q.answer_at = datetime.now()
        q.tags = form.tag.data
        q.topics = form.topic.data
        q.sub_topics = form.sub_topic.data
        q.answer_approved = form.approve.data
        q.answer_approve_user_id = current_user.id
        q.active = True
        q.answer_approved_at = convert_datetime_to_local(datetime.utcnow())
        try:
            db.session.commit()
            flash('Pergunta aprovada com sucesso', category='success')
            return redirect(url_for('question.view', id=q.id))
        except Exception as e:
            form.question.errors.append('Não foi possível atualizar')
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            return render_template('answer.html', form=form, approve=True)
                
    form.question.data = q.question
    form.answer.data = q.answer
    form.tag.data = q.tags
    form.topic.data = q.topics
    form.sub_topic.data = q.sub_topics
    form.approve.data = q.answer_approved
    form.answered_by.data = q.answered_by.name


    return render_template('answer.html', form=form, approve=True)

@bp.route('/tag/<string:name>')
@counter
def tag(name):
    topic = Topic.query.filter(Topic.name == g.selected_access).first()
    if topic is None:
        return redirect(url_for('main.select_access'))
    
    page = request.args.get('page', 1, type=int)
    search_form = QuestionSearchForm()
    pagination_args = {'name':name}
    tag = Tag.query.filter_by(name=name).first_or_404()
    paginate = db.session.query(Question).filter(Question.tags.contains(tag), Question.answer_approved == True).join(Question.topics).filter(Topic.id == topic.id).paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None

    url_args = dict(request.args)
    url_args.pop('page') if 'page' in url_args.keys() else None
    url_args['name'] = name

    return render_template('question.html', 
                                pagination=paginate, 
                                cls_question=Question, 
                                form=search_form, mode='views', 
                                first_page=first_page, 
                                last_page=last_page, 
                                url_args=url_args)

#TODO: REMOVER
@bp.route('/topic/<string:name>/<string:type>/')
@counter
def topic(name, type):
    if name != g.selected_access and current_user.is_anonymous:
        abort(404)
    page = request.args.get('page', 1, type=int)
    search_form = QuestionSearchForm()
    pagination_args = {'name':name, 'type': type}

    url_args = dict(request.args)
    url_args.pop('page') if 'page' in url_args.keys() else None
    try:
        pagination_args = pagination_args | url_args
    except TypeError:
        pagination_args = dict(pagination_args.items() | url_args.items())

    print(pagination_args)
    print(url_for('question.topic', page=1, **pagination_args))
    print(request.endpoint)
    topic = Topic.query.filter(Topic.name==name).first_or_404()
    if type in ['pendente', 'aprovada']:
        if type == 'pendente':
            paginate = topic.questions.filter(Question.answer != None, Question.answer_approved == False)
        if type == 'aprovada':
            paginate = topic.questions.filter(Question.answer_approved == True)
        paginate =  paginate.paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    else:
        return abort(404)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None

    url_args = dict(request.args)
    url_args.pop('page') if 'page' in url_args.keys() else None

    url_args['name'] = name
    url_args['type'] = type
    print(url_args)
    return render_template('question.html', 
                                pagination=paginate, 
                                cls_question=Question, 
                                form=search_form, mode='views', 
                                first_page=first_page, 
                                last_page=last_page, 
                                url_args=url_args)
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

@bp.route('/save/<int:question_id>', methods=['GET','POST'])
@login_required
def save_action(question_id):
    question = Question.query.filter(Question.id==question_id).first_or_404()
    action = request.form.get('action', False)
    if action is False or action not in ['save', 'unsave']:
        return jsonify({
            'status':'error',
            'message': 'ação inválida'}), 404
    if action == 'save':
        if question.is_saved(current_user.id):
            return jsonify({
                'status':'error',
                'message': 'Usuário já salvou dessa questão'}), 404
        rs = question.add_save(current_user.id)
        if rs is False:
            return jsonify({
                'status':'error',
                'message': 'Usuário já salvou dessa questão'}), 404
        return jsonify({
                'status':'success',
                'message': 'Ação concluída'}), 200
    if action == 'unsave':
        if not question.is_saved(current_user.id):
            return jsonify({
                'status':'error',
                'message': 'Usuário não salvou essa questão'}), 404
        rs = question.remove_save(current_user.id)
        if rs is False:
            return jsonify({
                'status':'error',
                'message': 'Não foi possível remover o gostar'}), 404
        return jsonify({
                'status':'success',
                'message': 'Ação concluída'}), 200





@bp.route('/likes')
@login_required
def likes():
    page = request.args.get('page', 1, type=int)
    questions = Question.likes_by_user(current_user.id, topic=g.topic)
    if questions is None:
        abort(404)
    paginate = questions.paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)

    # paginate = Question.query.order_by(Question.create_at.desc()).paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None
    return render_template('question.html', pagination=paginate, cls_question=Question, mode='views', first_page=first_page, last_page=last_page)
@bp.route('/saves')
@login_required
def saves():
    page = request.args.get('page', 1, type=int)
    questions = Question.saves_by_user(current_user.id, topic=g.topic)
    if questions is None:
        abort(404)
    paginate = questions.paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)

    # paginate = Question.query.order_by(Question.create_at.desc()).paginate(per_page=app.config.get('QUESTIONS_PER_PAGE'), page=page)
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None
    return render_template('question.html', pagination=paginate, cls_question=Question, mode='views', first_page=first_page, last_page=last_page)

    
@bp.route('/saved')
@login_required
def saved():
    ...
@bp.route('/perguntar', methods=['GET', 'POST'])
@counter
def make_question():   
    form = CreateQuestion()
    if form.validate_on_submit():
        question = Question.query.filter(Question.question.ilike(form.question.data)).first()
        sub_topic = SubTopic.query.all()
        question = Question.search(form.question.data, sub_topics=sub_topic)
        if question.count() > 0:
            flash('Já temos perguntas cadastras sobre o assunto pesquisado!!', category='warning')
            return redirect(url_for('question.search', q=form.question.data))
        if not form.errors:
            if current_user.is_authenticated:
                user = current_user
            else:
                user = User.query.filter(User.id == app.config.get('USER_ANON_ID', False)).first()
            ip = Network.query.filter(Network.ip == request.remote_addr).first()
            if ip is None:
                ip = Network()
                ip.ip = request.remote_addr
                db.session.add(ip)
                try:
                    db.session.commit()
                    return redirect(url_for('question.index'))
                except Exception as e:
                    db.session.rollback()
                    flash('Erro ao cadastrar o seu IP', category='success')
                    app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                    app.logger.error(e)
                    return abort(500)
            

            question = Question()
            topic = Topic.query.filter(Topic.name == g.selected_access).first()
            if topic is None:
                app.logger.error(f"Tópico {g.selected_access} não existe")
                return abort(500)  
            # print(topic)
            question.create_at = convert_datetime_to_local(datetime.utcnow())
            question.question = form.question.data
            question.topics.append(topic)
            question.sub_topic = form.sub_topic.data
            question.create_user_id = user.id
            question.question_network_id = ip.id
            question.active = True
            db.session.add(question)
            try:
                db.session.commit()
                flash(f'Dúvida cadastrada com sucesso! ID: {question.id}', category='success')
                return redirect(url_for('question.index'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return abort(500)
    return render_template('question.html', mode='make_question', form=form)
