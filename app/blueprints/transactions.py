from flask import Blueprint
from flask_login import login_required
from flask_security import roles_accepted

from app.utils.routes import counter
bp = Blueprint('transactions', __name__, url_prefix='/transacoes')

@bp.route('/')
@bp.route('/index')
@login_required
@roles_accepted('admin', 'support')
def index():
    return 'none'


@bp.route('/add')
@login_required
@roles_accepted('admin', 'support')
def add():
    return 'none'

@bp.route('/edit')
@login_required
@roles_accepted('admin', 'support')
def edit():
    return 'none'