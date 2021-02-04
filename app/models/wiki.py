# from sqlalchemy import func
from flask import Markup, escape, current_app as app, abort
from sqlalchemy import func, text, Index, cast, desc
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from markdown2 import markdown
from bs4 import BeautifulSoup
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils.types import TSVectorType

from sqlalchemy_searchable import make_searchable

from app.core.db import db
from app.utils.kernel import format_elapsed_time, get_list_max_len, only_letters
from app.utils.html import process_html
from app.models.security import User


make_searchable(db.metadata, options={'regconfig': 'pg_catalog.portuguese'})

def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return func.to_tsvector('portuguese', exp)


article_tag = db.Table('article_tag',
                       db.Column('post_id', db.Integer,
                                 db.ForeignKey('article.id')),
                       db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))


class ArticleView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey(
        'article.id'), nullable=False)
    first_view = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_view = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    count_view = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Article View id {self.article_id} by {self.user_id}>'


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), index=True, nullable=False, unique=True)
    description = db.Column(db.String(128), index=False, nullable=False)
    _text = db.Column(db.Text, index=False, nullable=False)
    create_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_at = db.Column(db.DateTime, index=True)
    update_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    # updater = db.relationship('User', foreign_keys = [update_user_id], backref='articles_updated')
    # author = db.relationship('User', foreign_keys = [user_id], backref='articles', lazy='dynamic')
    search_vector = db.Column(TSVectorType('_text', 'title', regconfig='pg_catalog.portuguese'))
    # __ts_vector__ = create_tsvector(
    #     cast(func.coalesce(_text, ''), postgresql.TEXT))

    # __table_args__ = (Index(
    #     'idx_text_fts',
    #     __ts_vector__,
    #     postgresql_using='gin'),)

    tags = db.relationship('Tag',
                           secondary=article_tag,
                           backref=db.backref('articles',
                                              lazy='dynamic'),
                           lazy='dynamic')

    views = db.relationship('ArticleView', cascade='all, delete-orphan',
                            backref='article', single_parent=True, lazy='dynamic')

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


    def search(text):
        # result = (db.session.query(Article, (func.strict_word_similarity(Article.text, 'principal')).label('similarity')).order_by(desc('similarity')))
        result = (db.session.query(Article, (
            func.ts_rank_cd(
                Article.search_vector, 
                func.plainto_tsquery(
                    'pg_catalog.portuguese',
                    text))).label(
                        'similarity')).filter((
            func.ts_rank_cd(
                Article.search_vector, 
                func.plainto_tsquery(
                    'pg_catalog.portuguese',
                    text))) > 0).order_by(
                    desc('similarity'))).all()
        return result

    def get_body_html(self, resume=False, size=256):
        html_classes = {'table': 'table table-bordered',
                        'img': 'img img-fluid'}
        if resume:
            l_text = list(filter(lambda x: x not in [
                          '', ' ', '\t'], self.text.split('\n')))
            # text = get_list_max_len(l_text, 256)
            return Markup(process_html(markdown('\n'.join(l_text), extras={"tables": None, "html-classes": html_classes}))).striptags()[0:size] + '...'
            # return Markup(process_html(markdown(text))).striptags()

        return Markup(process_html(markdown(self.text, extras={"tables": None, "html-classes": html_classes})))

    @property
    def get_text_resume(self):
        return self.get_body_html(resume=True, size=15)

    @property
    def format_create_date(self):
        return self.create_at.strftime("%d/%m/%Y")

    @property
    def get_create_time_elapsed(self):
        return format_elapsed_time(self.create_at)

    @property
    def get_update_time_elapsed(self):
        return format_elapsed_time(self.update_at)

    def add_view(self, user_id=None):
        if not user_id is None:
            user = User.query.filter_by(id=user_id).first_or_404()
            user_id = user.id
        article_view = ArticleView.query.filter_by(
            user_id=user_id, article_id=self.id).first()
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

    def sum_views(self, user_id: int = None):
        try:
            sum_query = db.session.query(
                func.sum(ArticleView.count_view).label('views')).join(Article.views)
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
                app.logger.error(app.config.get(
                    '_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return abort(500)
            return sum([x.views for x in rs if x.views != None])
        else:
            try:
                rs = sum_query.filter(ArticleView.article_id == self.id).filter(
                    ArticleView.user_id == user_id).all()
            except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get(
                    '_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return abort(500)
            return sum([x.views for x in rs if x.views != None])

    def was_updated(self):
        if self.update_at is None and self.update_user_id is None:
            return False
        return True

    @staticmethod
    def most_viewed():
        try:
            rs = db.session.query(Article, func.sum(ArticleView.count_view).label('views')).join(
                Article.views).group_by(Article).order_by(text('views DESC')).all()
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return abort(500)
        return [x[0] for x in rs if x != None]


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(32), index=True, nullable=False, unique=True)
    format_name = db.Column(db.String(32), index=True,
                            nullable=True, unique=True)
    create_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    articles = db.relationship('Article', backref='topic', lazy='dynamic')

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, text):
        self._name = text
        self.format_name = only_letters(text)

    def __repr__(self):
        return f'<Topic {self.name}>'


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(48), index=True, nullable=False)
    create_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Question(db.Model):
    '''
    Classe responsável pelas perguntas da wiki, com indexação para ``full text search``
    '''
    __searchable__ = ['question', 'answer']
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(256), index=True,
                         nullable=False, unique=True)
    answer = db.Column(db.Text, index=True, nullable=True, unique=False)
    create_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    create_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    update_at = db.Column(db.DateTime)
    update_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_at = db.Column(db.DateTime)

    search_vector = db.Column(TSVectorType('question', 'answer', regconfig='pg_catalog.portuguese'))

    view = db.relationship('QuestionView', backref='question', lazy='dynamic')
    like = db.relationship('QuestionLike', backref='question', lazy='dynamic')

    def __repr__(self):
        return f'<Question {self.question if len(self.question) <= 15 else self.question[:15] + "..."}>'


    def add_view(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        qv = QuestionView.query.filter(QuestionView.question_id==self.id, QuestionView.user_id==user.id).first()
        if qv == None:
            qv = QuestionView()
            qv.user_id = user_id
            qv.question_id = self.id
            qv.last_view = datetime.utcnow()
            qv.count_view = 1
            db.session.add(qv)
        else:
            qv.count_view += 1
            qv.last_view = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
        return qv
        

    @property
    def views(self):
        return db.session.query(func.sum(QuestionView.count_view)).filter(QuestionView.question_id==self.id).scalar()



    @property
    def likes(self):
        return db.session.query(func.sum(QuestionLike.question_id)).filter(QuestionLike.question_id==self.id).scalar()


    @property
    def answered(self):
        if self.answer != None:
            return True
        return False

    # def get_answer_html(self, resume=False, size=256):
    #     html_classes = {'table': 'table table-bordered',
    #                     'img': 'img img-fluid'}
    #     if self.answer is None:
    #         return ''
    #     if resume:
    #         l_text = list(filter(lambda x: x not in [
    #                       '', ' ', '\t'], self.answer.split('\n')))
    #         # text = get_list_max_len(l_text, 256)
    #         return Markup(process_html(markdown('\n'.join(l_text), extras={"tables": None, "html-classes": html_classes}))).striptags()[0:size] + '...'
    #         # return Markup(process_html(markdown(text))).striptags()

    #     return Markup(process_html(markdown(self.answer, extras={"tables": None, "html-classes": html_classes})))

    # @property
    # def answer_text(self):
    #     return self.get_answer_html(resume=9999)


class QuestionView(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,  db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    first_view = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_view = db.Column(db.DateTime, index=True, nullable=False)
    count_view = db.Column(db.Integer, default=1)

    


    def __repr__(self):
        return f'<Question View id: {self.question_id} by {self.user_id}>'

    
    def views_by_question(self, question_id : int):
        return db.session.query(func.sum(QuestionView.count_view)).filter(QuestionView.question_id == question_id).scalar()

    def views_by_user(self, user_id : int):
        return db.session.query(func.sum(QuestionView.count_view)).filter(QuestionView.user_id == user_id).scalar()


class QuestionLike(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Question Like id: {self.question_id} by {self.user_id}>'

    def likes_by_user(self, question_id : int):
        return self.query.filter(self.question_id == question_id).count()

    def likes_by_user(self, user_id : int):
        return self.query.filter(self.question_id == user_id).count()

class QuestionSave(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Question Like id: {self.question_id} by {self.user_id}>'

    def saves_by_user(self, question_id : int):
        return self.query.filter(self.question_id == question_id).count()

    def saves_by_user(self, user_id : int):
        return self.query.filter(self.question_id == user_id).count()

# TESTE
# (db.session.query(Article, func.ts_rank('{0.1,0.1,0.1,0.1}', Article._text, func.to_tsquery('smit:* | ji:*')).label('rank'))
#     .filter(Article._text.op('@@')(func.to_tsquery('smit:* | ji:*')))
#     .order_by('rank desc')
#  ).all()


# subquery = db.session.query(
#     Article,
#     func.ts_rank().over(order_by=Article.create_at.desc(),
#                      partition_by=Article.id
#                      ).label('rnk')
# ).subquery()

# query = db.session.query(subquery).filter(
#     subquery.c.rnk >= 1
# )


# (db.session.query(User, func.ts_rank('{0.1,0.1,0.1,0.1}', User.textsearchable_index_col, func.to_tsquery('smit:* | ji:*')).label('rank'))
#     .filter(User.authentication_method != 2)
#     .filter(User.textsearchable_index_col.op('@@')(func.to_tsquery('smit:* | ji:*')))
#     .order_by('rank desc')
# ).all()

# (db.session.query(Article, func.ts_rank('{0.1,0.1,0.1,0.1}', Article.search_vector, func.to_tsquery('comportamento')).label('rank'))
#     .filter(Article.search_vector.op('@@')(func.to_tsquery('comportamento')))
#     .order_by('rank desc')
#  ).all()

# (db.session.query(Article, func.ts_rank('{0.1,0.1,0.1,0.1}', Article.__ts_vector__, func.to_tsquery('mutacao')).label('rank'))
#     .filter(Article.__ts_vector__.op('@@')(func.to_tsquery('mutacao')))
#     .order_by('rank')
#  ).all()
# 
# 

# (db.session.query(Article, func.ts_rank('{0.1,0.1,0.1,0.1}', Article.search_vector, func.to_tsquery('tres')).label('rank'))
#     .filter(Article.search_vector.op('@@')(func.to_tsquery('tres')))
#     .order_by('rank')
#  ).all()


# (db.session.query(Article, (func.strict_word_similarity(Article.search_vector.op('@@')(func.to_tsquery('principal'), 'principal')).label('sml'))).order_by(desc('sml'))).all()

# (db.session.query(Article, (func.strict_word_similarity(Article.text, 'principal variantes sobre tempo exemplo')).label('sml'))).order_by(desc('sml')).all()