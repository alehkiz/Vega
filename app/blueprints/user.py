from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, request, g
from flask_security import current_user, login_user, logout_user

bp = Blueprint('user', __name__, url_prefix='/user/')

@bp.route('/')
@bp.route('/index/')
def index():
    return render_template('base.html')

@bp.route('/<name>')
def view(name):
    return render_template('base.html')