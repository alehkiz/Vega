from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, abort, request, escape, g, jsonify
from flask.globals import current_app
from flask_security import login_required, current_user
from flask_security import roles_accepted
from app.core.db import db
from app.models.wiki import Question, QuestionLike, QuestionSave, QuestionView, Tag
from app.models.security import User
from app.models.search import Search

bp = Blueprint('api', __name__, url_prefix='/api/')

@bp.route('question/<int:id>', methods=['GET', 'POST'])
def question(id):
    question = Question.query.filter(Question.id==id).first_or_404()
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