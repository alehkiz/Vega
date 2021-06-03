from flask import Blueprint, render_template, request, jsonify

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(404)
def handler_error_404(err):
    if request.path.startswith('/api/'):
        return jsonify(error=str(err)), err.code
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def handler_error_500(err):
    if request.path.startswith('/api/'):
        return jsonify(error=str(err)), err.code
    return render_template('500.html'), 500