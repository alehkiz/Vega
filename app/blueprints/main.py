from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json
from flask_security import login_required, current_user


bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    return 'ola mundo '

@bp.route('/main')
def main():
    return 'teste'