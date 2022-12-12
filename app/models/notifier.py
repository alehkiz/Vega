from datetime import datetime
from sqlalchemy.orm import backref
from sqlalchemy_searchable import make_searchable
from flask import url_for

from app.core.db import db
from app.utils.kernel import format_datetime_local, format_elapsed_time, convert_datetime_to_local
from app.utils.others import limit_chars


make_searchable(db.metadata, options={'regconfig': 'public.pt'})




notifier_topic = db.Table('notifier_topic', db.Column('notifier_id', db.Integer, db.ForeignKey(
    'notifier.id')), db.Column('topic_id', db.Integer, db.ForeignKey('topic.id')))

class Notifier(db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True, nullable=False, unique=False)
    content = db.Column(db.String, index=True, nullable=False)
    autoload = db.Column(db.Boolean, nullable=False, default=False)
    status_id = db.Column(db.Integer, db.ForeignKey(
        'notifier_status.id'), nullable=False)
    priority_id = db.Column(db.Integer, db.ForeignKey(
        'notifier_priority.id'), nullable=False)
    create_at = db.Column(db.DateTime, index=False,
                          default=convert_datetime_to_local(datetime.utcnow()))
    created_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    topics = db.relationship('Topic',
                             secondary=notifier_topic,
                             backref=db.backref('notifications',
                                                lazy='dynamic', cascade='save-update', single_parent=True), lazy='dynamic')
    # topics = db.relationship('Topic',
    #                          secondary=transaction_topic,
    #                          backref=db.backref('transactions',
    #                                             lazy='dynamic', cascade='save-update', single_parent=True), lazy='dynamic')
    # topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    created_network_id = db.Column(
        db.Integer, db.ForeignKey('network.id'), nullable=False)
    update_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # status = db.relationship('NotifierStatus', single_parent=True, backref='notices', lazy='dynamic')

    @property
    def get_create_time_elapsed(self):
        return format_elapsed_time(self.create_at)

    @property
    def get_formated_date(self):
        return format_datetime_local(self.create_at)

    @property
    def topics_name(self):
        if not self.topics.all():
            return None
        return [x.name for x in self.topics.all()]

    @property
    def priority_name(self):
        if self.priority is None:
            return None
        return self.priority.priority

    @property
    def priority_order(self):
        if self.priority is None:
            return None
        return self.priority.order

    @property
    def status_name(self):
        if self.status is None:
            return None
        return self.status.status

    @property
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': limit_chars(self.content, 50),
            'status': self.status_name,
            'priority_order': self.priority_order,
            'url' : url_for('api.notification', id=self.id)
        }

    @property
    def to_dict_detail(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status_name,
            'priority': self.priority_name,
            'priority_order': self.priority_order,
            'created_elapsed_time': self.get_create_time_elapsed
        }
    def __repr__(self) -> str:
        return super().__repr__()


class NotifierStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32), nullable=False)
    notices = db.relationship('Notifier', backref='status', lazy='dynamic')


class NotifierPriority(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String(32), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    notices = db.relationship('Notifier', backref='priority', lazy='dynamic')
