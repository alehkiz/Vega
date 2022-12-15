from flask import Blueprint, render_template, request, jsonify, g 
from app.forms.search import SearchForm

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(404)
def handler_error_404(err):
    if request.path.startswith('/api/'):
        return jsonify(error=str(err)), err.code
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def handler_error_500(err):
    if request.path.startswith('/api/'):
        return jsonify(error=str(err)), err.code
    return render_template('errors/500.html'), 500


@bp.app_errorhandler(413)
def handler_error_413(err):
    g.search_form = SearchForm()
    g.question_search_form = SearchForm()
    if request.path.startswith('/api/'):
        return jsonify(error=str(err)), err.code
    return render_template('errors/413.html'), 413