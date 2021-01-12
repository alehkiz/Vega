from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json



bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login')
def login():
    return 'login'
