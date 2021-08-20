from flask import Blueprint, render_template


bp = Blueprint('notifier', __name__, url_prefix='/notificacao')

@bp.route('/')
def index():
    return render_template('notifier.html')