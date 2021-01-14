from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup
from flask_security import login_required, current_user


bp = Blueprint('wiki', __name__, url_prefix='/wiki/')

@bp.route('/')
@bp.route('/index')
@bp.route('/<article_id>')
def wiki(article_id):
    return ''