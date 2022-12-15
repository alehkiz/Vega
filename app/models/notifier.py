from datetime import datetime
from sqlalchemy.orm import backref
from sqlalchemy_searchable import make_searchable
from flask import url_for, Markup
from bs4 import BeautifulSoup as bs
from markdown2 import markdown
from app.core.db import db
from app.utils.html import process_html, replace_newline_with_br
from app.utils.kernel import format_datetime_local, format_elapsed_time, convert_datetime_to_local
from app.utils.others import limit_chars


make_searchable(db.metadata, options={'regconfig': 'public.pt'})


notifier_sub_topic = db.Table('notifier_sub_topic',
                        db.Column('notifier_id', db.Integer, 
                                    db.ForeignKey('notifier.id')),
                        db.Column('sub_topic_id', db.Integer, db.ForeignKey('sub_topic.id'))
                        )

notifier_topic = db.Table('notifier_topic', 
                        db.Column('notifier_id', db.Integer, 
                                    db.ForeignKey('notifier.id')),
                        db.Column('topic_id', db.Integer, db.ForeignKey('topic.id')))

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
    level_id = db.Column(db.Integer, db.ForeignKey(
        'notifier_level.id'), nullable=False)
    create_at = db.Column(db.DateTime, index=False,
                          default=convert_datetime_to_local(datetime.utcnow()))
    closed_at = db.Column(db.DateTime, index=False,
                          nullable=True)
    created_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    topics = db.relationship('Topic',
                             secondary=notifier_topic,
                             backref=db.backref('notifications',
                                                lazy='dynamic', cascade='save-update', single_parent=True), lazy='dynamic')
    sub_topics = db.relationship('SubTopic', 
                                secondary=notifier_sub_topic, 
                                backref=db.backref('notifications', 
                                                    lazy='dynamic', cascade='save-update', single_parent=True), lazy='dynamic')
    created_network_id = db.Column(
        db.Integer, db.ForeignKey('network.id'), nullable=False)
    update_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def get_create_time_elapsed(self):
        return format_elapsed_time(self.create_at)

    @property
    def get_formated_date(self):
        return format_datetime_local(self.create_at)

    @property
    def get_content_text(self):
        html = bs(self.content)
        return html.get_text()
    @property
    def topics_name(self, as_string=True):
        if not self.topics.all():
            return None
        if as_string == True:
            return ', '.join([x.name for x in self.topics.all()])
        return [x.name for x in self.topics.all()]

    @property
    def priority_name(self):
        if self.priority is None:
            return None
        return self.priority.priority
    @property
    def level_translate_name(self):
        if self.level is None:
            return None
        return self.level.level_translate
    @property
    def level_bootstrap_name(self):
        if self.level is None:
            return None
        return self.level.level_bootstrap

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
    def get_autoload(self):
        return "Sim" if self.autoload else "Não"
    def get_body_html(self, resume=False, size=1500):
        html_classes = {'table': 'table table-bordered',
                        'img': 'img img-fluid'}
        if resume:
            l_text = list(filter(lambda x: x not in [
                          '', ' ', '\t'], self.content.split('\n')))
            # text = get_list_max_len(l_text, 256)
            return Markup(process_html(markdown('\n'.join(l_text), 
                                            extras={"tables": None, "html-classes": html_classes, 'target-blank-links':True}))).striptags()[0:size] + '...'
            # return Markup(process_html(markdown(text))).striptags()

        return Markup(markdown(self.content, extras={"tables": None, "html-classes": html_classes, 'target-blank-links':True}))
    @property
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': limit_chars(self.get_body_html(), 50),
            'status': self.status_name,
            'level': self.level_bootstrap_name,
            'priority_order': self.priority_order,
            'url' : url_for('api.notification', id=self.id),
            'subtopic': '' if self.sub_topics.first() is None else self.sub_topics.first().name
        }

    @property
    def to_dict_detail(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.get_body_html(),
            'status': self.status_name,
            'level': self.level_bootstrap_name,
            'priority': self.priority_name,
            'priority_order': self.priority_order,
            'created_elapsed_time': self.get_create_time_elapsed,
            'subtopic': '' if self.sub_topics.first() is None else self.sub_topics.first().name
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

class NotifierLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_bootstrap = db.Column(db.String(12), nullable=False)
    level_translate = db.Column(db.String(12), nullable=False)
    notices = db.relationship('Notifier', backref='level', lazy='dynamic')