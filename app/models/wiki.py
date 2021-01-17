from flask import Markup, escape
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from markdown import markdown
from app.core.db import db
from app.utils.kernel import format_elapsed_time, get_list_max_len
from app.utils.html import process_html
from bs4 import BeautifulSoup

article_tag = db.Table('article_tag',
                        db.Column('post_id', db.Integer, db.ForeignKey('article.id')),
                        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), index=True, nullable=False, unique=True)
    description = db.Column(db.String(128), index=False, nullable=False)
    _text = db.Column(db.Text, index=False, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    tags = db.relationship('Tag', 
            secondary=article_tag, 
            backref=db.backref('articles', 
                lazy='dynamic'), 
            lazy='dynamic')

    @hybrid_property
    def text(self):
        return self._text
        
    @text.setter
    def text(self, text):
        '''
        Remove tags html in text
        '''
        self._text = BeautifulSoup(text).get_text()

    def __repr__(self):
        return f'<Article {self.title}>'

    def get_body_html(self, resume=False):
        if resume:
            l_text = list(filter(lambda x : x not in ['', ' ', '\t'], self.text.split('\n')))
            text = get_list_max_len(l_text, 256)
            print(text)
            return Markup(process_html(markdown('\n'.join(text)))).striptags()
            # return Markup(process_html(markdown(text))).striptags()
        return Markup(process_html(markdown(self.text)))

    def get_time_elapsed(self):
        return format_elapsed_time(self.timestamp)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    articles = db.relationship('Article', backref='topic', lazy='dynamic')

    def __repr__(self):
        return f'<Topic {self.name}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(48), index=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))