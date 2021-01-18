from flask import Markup, escape, current_app as app, abort
from sqlalchemy import func, text
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from markdown2 import markdown
from bs4 import BeautifulSoup


from app.core.db import db
from app.utils.kernel import format_elapsed_time, get_list_max_len, only_letters
from app.utils.html import process_html
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
    updated_timestamp = db.Column(db.DateTime, index=True)
    updated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    # updater = db.relationship('User', foreign_keys = [updated_user_id], backref='articles_updated')
    # author = db.relationship('User', foreign_keys = [user_id], backref='articles', lazy='dynamic')
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
        self._text = BeautifulSoup(text, features="lxml").get_text()

    def __repr__(self):
        return f'<Article {self.title}>'

    def get_body_html(self, resume=False):
        if resume:
            l_text = list(filter(lambda x : x not in ['', ' ', '\t'], self.text.split('\n')))
            text = get_list_max_len(l_text, 256)
            return Markup(process_html(markdown('\n'.join(text)))).striptags()
            # return Markup(process_html(markdown(text))).striptags()
        html_classes = {'table': 'table table-bordered',
                        'img': 'img img-fluid'}
        return Markup(process_html(markdown(self.text, extras={"tables": None, "html-classes":html_classes})))

    def get_time_elapsed(self):
        return format_elapsed_time(self.timestamp)
    def get_update_elapsed(self):
        return format_elapsed_time(self.updated_timestamp)
    def add_view(self, user_id=None):
        if not user_id is None:
            user = User.query.filter_by(id=user_id).first_or_404()
            user_id = user.id
        article_view = ArticleView.query.filter_by(user_id=user_id, article_id=self.id).first()
        if article_view is None:
            article_view = ArticleView()
            article_view.article_id = self.id
            article_view.user_id = user_id
            self.views.append(article_view)
        else:
            article_view.count_view += 1
            article_view.last_view = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return abort(500)
    def sum_views(self, user_id : int=None):
        try:
            sum_query = db.session.query(func.sum(ArticleView.count_view).label('views')).join(Article.views)
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return abort(500)
        if user_id is None:
            try:
                rs = sum_query.filter(ArticleView.article_id == self.id).all()
            except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return abort(500)
            return sum([x.views for x in rs if x.views != None])
        else:
            try:
                rs = sum_query.filter(ArticleView.article_id == self.id).filter(ArticleView.user_id == user_id).all()
            except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return abort(500)
            return sum([x.views for x in rs if x.views != None])
    @staticmethod
    def most_viewed():
        try:
            rs = db.session.query(Article, func.sum(ArticleView.count_view).label('views')).join(Article.views).group_by(Article).order_by(text('views DESC')).all()
        except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return abort(500)
        return [x[0] for x in rs if x != None]
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(32), index=True, nullable=False, unique=True)
    formated_name = db.Column(db.String(32), index=True, nullable=True, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    articles = db.relationship('Article', backref='topic', lazy='dynamic')

    @hybrid_property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, text):
        self._name = text
        self.formated_name = only_letters(text)

    def __repr__(self):
        return f'<Topic {self.name}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(48), index=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))