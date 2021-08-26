from app.models.notifier import Notifier, NotifierPriority, NotifierStatus
from flask import Blueprint, render_template
from app.core.db import db


bp = Blueprint('notifier', __name__, url_prefix='/notificacao')

@bp.route('/')
def index():
    notices_active = db.session.query(Notifier).join(NotifierStatus, Notifier.status).join(NotifierPriority, Notifier.priority).filter(NotifierStatus.status == 'Ativo').order_by(NotifierPriority.id.asc())
    # Notifier.query.filter(NotifierStatus.status == 'Ativo')
    notices_history = db.session.query(Notifier).join(NotifierStatus, Notifier.status).filter(NotifierStatus.status == 'Histórico').order_by(NotifierPriority.id.asc())
    # Notifier.query.filter(NotifierStatus.status == 'Histórico')
    return render_template('notifier.html', notices_active = notices_active, notices_history = notices_history)