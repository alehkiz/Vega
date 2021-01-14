from flask import Blueprint, render_template

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(404)
def handler_error_404(err):
    return render_template('404.html'), 404

@bp.app_errorhandler(400)
def handler_error_500(err):
    return render_template('500.html'), 500