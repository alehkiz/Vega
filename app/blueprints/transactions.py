from flask import Blueprint

from app.utils.routes import counter
bp = Blueprint('transactions', __name__, url_prefix='/transações')

@bp.route('/')
@bp.route('/index')
@counter
def index():
    return 'none'