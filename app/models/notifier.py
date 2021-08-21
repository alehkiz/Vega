from datetime import datetime
from sqlalchemy.orm import backref
from sqlalchemy_searchable import make_searchable

from app.core.db import db
from app.utils.kernel import format_elapsed_time

make_searchable(db.metadata, options={'regconfig': 'public.pt'})


class Notifier(db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, nullable=False, unique=False)
    content = db.Column(db.String, index=True, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('notifier_status.id'), nullable=False)
    create_at = db.Column(db.DateTime, index=False, default=datetime.utcnow)
    created_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    # status = db.relationship('NotifierStatus', single_parent=True, backref='notices', lazy='dynamic')
    

    def __repr__(self) -> str:
        return super().__repr__()

class NotifierStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32), nullable=False)
    notices = db.relationship('Notifier', backref='status', lazy='dynamic')