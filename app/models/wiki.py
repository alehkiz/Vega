from flask import Markup, escape, current_app as app, abort
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from markdown import markdown
from app.core.db import db
from app.utils.kernel import format_elapsed_time, get_list_max_len
from app.utils.html import process_html
from bs4 import BeautifulSoup
from app.models.security import User

article_tag = db.Table('article_tag',
                        db.Column('post_id', db.Integer, db.ForeignKey('article.id')),
                        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))

class ArticleView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id =db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    first_view = db.Column(db.DateTime, index=True, default= datetime.utcnow)
    last_view = db.Column(db.DateTime, index=True, default= datetime.utcnow)
    count_view = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Article View id {self.article_id} by {self.user_id}'

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

    views = db.relationship('ArticleView', cascade='all, delete-orphan', backref='article', single_parent=True, lazy='dynamic')
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
    def view(self, user_id):
        user = User.query.filter_by(id=user_id).first_or_404()
        article_view = ArticleView.query.filter_by(user_id=user.id, article_id=self.id).first()
        if article_view is None:
            article_view = ArticleView()
            article_view.article_id = self.id
            article_view.user_id = user.id
            self.views.append(article_view)
        else:
            article_view.count_view += 1
            article_view.last_view = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return abort(500)


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