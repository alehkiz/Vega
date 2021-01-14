from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from markdown import markdown
# from pypandoc import convert_text
from app.core.db import db

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), index=True, nullable=False, unique=True)
    description = db.Column(db.String(128), index=False, nullable=False)
    text = db.Column(db.Text, index=False, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    def __repr__(self):
        return f'<Article {self.title}>'

    def get_description_html(self):
        return markdown(self.text)

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
    # articles = db.relationship('Article', )