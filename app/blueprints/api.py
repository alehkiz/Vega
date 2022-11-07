from app.models.app import Visit
import re
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request, escape, g, jsonify, session
from flask.globals import current_app
from flask_security import login_required, current_user
from flask_security import roles_accepted
from app.core.db import db
from app.models.notifier import Notifier, NotifierPriority, NotifierStatus
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView, Tag, Topic
from app.models.security import User
from app.models.app import Network
from app.models.search import Search
from app.utils.kernel import order_dict
from app.utils.routes import counter
from datetime import datetime
# import time

bp = Blueprint('api', __name__, url_prefix='/api/')

@bp.errorhandler(404)
def resource_not_found(e):
    return {'error_cod': 404, 'error': 'Não encontrado'}, 404
@bp.errorhandler(500)
def server_error(e):
    return {'error_cod': 500, 'error': 'Erro interno'}, 500

@bp.route('question/<int:id>', methods=['GET', 'POST'])
@counter
def question(id):
    if session.get("AccessType", False) is False:
        abort(500)
    # access_type = session.get("AccessType", False)
    question = Question.query.filter(Question.id == id).first()

    if question is None:
        return abort(404)
    if question.answer_approved == False or question.active != True or question.was_answered != True:
        abort(404)
    if current_user.is_authenticated:
        question.add_view(current_user.id, g.ip_id)
        to_dict = question.to_dict()
        if question.is_liked(current_user.id):
            to_dict['like_action'] = 'unlike'
        else:
            to_dict['like_action'] = 'like'
        if question.is_saved(current_user.id):
            to_dict['save_action'] = 'unsave'
        else:
            to_dict['save_action'] = 'save'
        to_dict['url_like'] = url_for('question.like_action', question_id=id)
        to_dict['url_save'] = url_for('question.save_action', question_id=id)
        if current_user.can_edit:
            to_dict['url_edit'] = url_for('question.edit', id=id)
    else:
        question.add_view(app.config.get('USER_ANON_ID'), g.ip_id)
        to_dict = question.to_dict()
    to_dict['url_view'] = url_for('question.view', id=id)
    return jsonify(to_dict)


@bp.route('json/questions/access')
def question_access():
    return ''

@bp.route('notifications')
@counter
def notifications():
    if session.get("AccessType", False) is False:
        abort(500)
    notifier = db.session.query(Notifier).join(NotifierStatus).join(NotifierPriority).filter(NotifierStatus.status == 'Ativo').order_by(NotifierPriority.order.asc())
    to_dict = [_.to_dict for _ in notifier]
    return jsonify(to_dict)
# # api dashboard
# @bp.route('dashboard/tags_data', methods=['GET', 'POST'])
# def tags_data():
#     '''
#     Gera dados das 10 maiores categorias, caso tenham mais de 10 categorias a 10ª será Outros
#     '''
#     questions = Tag._dict_count_questions()
#     questions = order_dict(Tag._dict_count_questions(), 5)
#     return jsonify({
#         'labels': list(questions.keys()),
#         'datasets': [{
#             'data': list(questions.values()),
#             'backgroundColor': [
#                 "blue",
#                 "purple",
#                 "pink",
#                 "red",
#                 "orange",
#                 "yellow",
#                 "green",
#                 "cyan",
#                 "gray",
#                 "black"
#             ]  # ,
#             # 'hoverBackgroundColor': [
#             #     "#CFD4D8",
#             #     "#B370CF",
#             #     "#E95E4F",
#             #     "#36CAAB",
#             #     "#49A9EA"
#             # ]
#         }],
#         'totalQuestions': Question.query.count()
#     })




# @bp.route('dashboard/visit', methods=['GET', 'POST'])
# def visits_by_interval():
#     if request.method == 'POST':
#         start = request.form.get('start', False)
#         end = request.form.get('end', False)
#         if start is False or end is False:
#             return jsonify({
#                 'error': True,
#                 'mensage': 'Data inicial ou final inválida;'
#             })
#         return jsonify([[_[1].strftime('%Y-%m-%dT%H:%M:%S.%f'),
#                         _[0]] for _ in Visit.total_by_date(start, end).all()])


# @bp.route('dashboard/visits', methods=['GET', 'POST'])
# def visits_data():
#     if request.method == 'POST':
#         year = request.form.get('year', False)
#         month = request.form.get('month', None)
#         start = request.form.get('start', False)
#         end = request.form.get('end', False)
#         if not year.isnumeric():
#             return jsonify({
#                 'error': True,
#                 'message': 'Ano inválido'
#             })
#         year = int(year)
#         if year is False:
#             return jsonify({
#                 'error': True,
#                 'message': 'Ano inválido'
#             })
#         if month is None:
#             return jsonify([[_[1].strftime('%Y-%m-%dT%H:%M:%S.%f'),_[0]] for _ in Visit.total_by_year_month(year=year).all()])
#             try:
#                 return jsonify({_[1]:_[0] for _ in Visit.total_by_year_month(year=year).all()})
#             except Exception as e:
#                 return jsonify({
#                     'error': True,
#                     'message': 'Valor inválido Mês'
#                 })
#         if not month.isnumeric():
#             return jsonify(
#                 {'error':True, 
#                 'message': 'Mês inválido'}
#             )
#         try:
#             month = int(month)
#             return jsonify([[_[1].strftime('%Y-%m-%dT%H:%M:%S.%f'),_[0]] for _ in Visit.total_by_year_month(year=year, month=month).all()])
#         except Exception as e:
#             return jsonify({
#                 'error': True,
#                 'message': 'Valor inválido'
#             })
#     return ''
