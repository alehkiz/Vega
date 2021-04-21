from app.models.app import Visit
import re
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request, escape, g, jsonify
from flask.globals import current_app
from flask_security import login_required, current_user
from flask_security import roles_accepted
from app.core.db import db
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView, Tag
from app.models.security import User
from app.models.search import Search
from app.utils.kernel import order_dict
# import time

bp = Blueprint('api', __name__, url_prefix='/api/')


@bp.route('question/<int:id>', methods=['GET', 'POST'])
def question(id):
    question = Question.query.filter(Question.id == id).first_or_404()
    if question.answer_approved == False:
        abort(404)
    to_dict = question.to_dict()
    if current_user.is_authenticated:
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
        question.add_view(current_user.id)
    else:
        # anon_user = User.query.filter_by(id=app.config.get('USER_ANON_ID')).first_or_404()
        question.add_view(app.config.get('USER_ANON_ID'))
    return jsonify(to_dict)


@bp.route('json/questions/access')
def question_access():
    return ''


# api dashboard
@bp.route('dashboard/tags_data', methods=['GET', 'POST'])
def tags_data():
    '''
    Gera dados das 10 maiores categorias, caso tenham mais de 10 categorias a 10ª será Outros
    '''
    questions = Tag._dict_count_questions()
    questions = order_dict(Tag._dict_count_questions(), 5)
    return jsonify({
        'labels': list(questions.keys()),
        'datasets': [{
            'data': list(questions.values()),
            'backgroundColor': [
                "blue",
                "purple",
                "pink",
                "red",
                "orange",
                "yellow",
                "green",
                "cyan",
                "gray",
                "black"
            ]  # ,
            # 'hoverBackgroundColor': [
            #     "#CFD4D8",
            #     "#B370CF",
            #     "#E95E4F",
            #     "#36CAAB",
            #     "#49A9EA"
            # ]
        }],
        'totalQuestions': Question.query.count()
    })


@bp.route('dashboard/visits', methods=['GET', 'POST'])
def visits_data():
    if request.method == 'POST':
        year = request.form.get('year', False)
        month = request.form.get('month', None)
        if not year.isnumeric():
            return jsonify({
                'erro': True,
                'message': 'Ano inválido'
            })
        year = int(year)
        print(year)
        if year is False:
            return jsonify({
                'erro': True,
                'message': 'Ano inválido'
            })
        if month is None:
            return jsonify([[_[1].strftime('%Y-%m-%dT%H:%M:%S.%f'),_[0]] for _ in Visit.total_by_date(year=year).all()])
            try:
                return jsonify({_[1]:_[0] for _ in Visit.total_by_date(year=year).all()})
            except Exception as e:
                return jsonify({
                    'erro': True,
                    'message': 'Valor inválido YEAR'
                })
        try:
            return Visit.total_by_date(year, month).all()
        except Exception as e:
            return jsonify({
                'erro': True,
                'message': 'Valor inválido'
            })
    return ''
