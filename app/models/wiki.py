# from sqlalchemy import func
from enum import unique
from os import stat
from flask import Markup, escape, current_app as app, abort, flash
from sqlalchemy import func, text, Index, cast, desc, extract, Date
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date, datetime
from markdown2 import markdown
from bs4 import BeautifulSoup
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.expression import false
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy.orm import backref, lazyload
from sqlalchemy.dialects.postgresql import INET

from sqlalchemy_searchable import make_searchable

from app.core.db import db
from app.utils.kernel import convert_datetime_to_local, format_elapsed_time, get_list_max_len, only_letters, format_datetime_local, days_elapsed, process_value
from app.utils.html import process_html
from app.models.security import User


make_searchable(db.metadata, options={'regconfig': 'public.pt'})


article_tag = db.Table('article_tag',
                       db.Column('post_id', db.Integer,
                                 db.ForeignKey('article.id')),
                       db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))

question_tag = db.Table('question_tag',
                        db.Column('question_id', db.Integer,
                                  db.ForeignKey('question.id')),
                        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))


question_topic = db.Table('question_topic',
                          db.Column('question_id', db.Integer,
                                    db.ForeignKey('question.id')),
                          db.Column('topic_id', db.Integer, db.ForeignKey('topic.id')))


class ArticleView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey(
        'article.id'), nullable=False)
    first_view = db.Column(db.DateTime(timezone=True), index=True, default=convert_datetime_to_local(datetime.utcnow()))
    last_view = db.Column(db.DateTime(timezone=True), index=True)
    count_view = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Article View id {self.article_id} by {self.user_id}>'


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), index=True, nullable=False, unique=True)
    description = db.Column(db.String(128), index=False, nullable=False)
    _text = db.Column(db.Text, index=False, nullable=False)
    create_at = db.Column(db.DateTime(timezone=True), index=True, default=convert_datetime_to_local(datetime.utcnow()))
    update_at = db.Column(db.DateTime(timezone=True), index=True)
    update_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    # updater = db.relationship('User', foreign_keys = [update_user_id], backref='articles_updated')
    # author = db.relationship('User', foreign_keys = [user_id], backref='articles', lazy='dynamic')
    search_vector = db.Column(TSVectorType(
        '_text', 'title', regconfig='public.pt', cache_ok=False))
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

    def search(text, pagination=False, per_page=1, page=1, resume=False):
        # result = (db.session.query(Article, (func.strict_word_similarity(Article.text, 'principal')).label('similarity')).order_by(desc('similarity')))
        if resume:
            result = (db.session.query(Article.title, (
                func.ts_rank_cd(
                    Article.search_vector,
                    func.plainto_tsquery(
                        'public.pt',
                        text))).label(
                            'similarity')).filter((
                                func.ts_rank_cd(
                                    Article.search_vector,
                                    func.plainto_tsquery(
                                        'public.pt',
                                        text))) > 0)  # .order_by(
                      # desc('similarity'))
                      )
        else:
            result = (db.session.query(Article, (
                func.ts_rank_cd(
                    Article.search_vector,
                    func.plainto_tsquery(
                        'public.pt',
                        text))).label(
                            'similarity')).filter((
                                func.ts_rank_cd(
                                    Article.search_vector,
                                    func.plainto_tsquery(
                                        'public.pt',
                                        text))) > 0)  # .order_by(
                      # desc('similarity'))
                      )
        if pagination:
            result = result.paginate(page=page, per_page=per_page)
        return result

    @property
    def resume(self):
        return self.title
    # def get_resume(self):
    #     return self.title

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
            article_view.last_view = datetime.now()
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
    def most_viewed(limit=5):
        try:
            rs = db.session.query(Article, func.sum(ArticleView.count_view).label('views')).join(
                Article.views).group_by(Article).order_by(text('views DESC')).limit(limit).all()
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
    active = db.Column(db.Boolean, default=True)
    create_at = db.Column(db.DateTime(timezone=True), index=True, default=convert_datetime_to_local(datetime.utcnow()))
    selectable = db.Column(db.Boolean, default=False, nullable=False)
    nickname = db.Column(db.String(10), nullable=False, unique=True)
    articles = db.relationship('Article', backref='topic', lazy='dynamic')
    # questions_old = db.relationship('Question', backref='topic', lazy='dynamic', foreign_keys='[Question.topic_id]')
    notices = db.relationship('Notifier', backref='topic', lazy='dynamic')

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, text):
        self._name = text
        self.format_name = only_letters(text)

    def __repr__(self):
        return f'<Topic {self.name}>'


class SubTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(32), index=True, nullable=False, unique=True)
    format_name = db.Column(db.String(32), index=True,
                            nullable=True, unique=True)
    create_at = db.Column(db.DateTime(timezone=True), index=True, default=convert_datetime_to_local(datetime.utcnow()))
    # articles = db.relationship('Article', backref='topic', lazy='dynamic')
    questions = db.relationship('Question', backref='sub_topic',
                                lazy='dynamic', foreign_keys='[Question.sub_topic_id]')

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
    name = db.Column(db.String(48), index=True, nullable=False, unique=True)
    create_at = db.Column(db.DateTime(timezone=True), index=True, default=convert_datetime_to_local(datetime.utcnow()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='tag')
    # questions = db.relationship('Question', backref=backref('tag', lazy='dynamic'), lazy='dynamic', foreign_keys='[Question.tag_id]')

    @hybrid_property
    def username(self):
        if self.user is None:
            return ''
        return self.user.name

    @staticmethod
    def _dict_count_questions():
        return {_.name: _.questions.count() for _ in Tag.query.all()}

    def questions_approved(self, topic=None):
        if topic != None:
            return db.session.query(Tag).join(Tag.questions).join(Question.topics).filter(Question.answer_approved == True, Topic.id== topic.id, Tag.id == self.id)
            # return self.questions.filter(Question.answer != None, Question.answer_approved == True, Question.topic_id == topic.id)
        return self.questions.filter(Question.answer != None, Question.answer_approved == True)


class Question(db.Model):
    '''
    Classe responsável pelas perguntas da wiki, com indexação para ``full text search``


    #cria configuração para remover acentos
    CREATE TEXT SEARCH CONFIGURATION pt (COPY = pg_catalog.portuguese);
    ALTER TEXT SEARCH CONFIGURATION pt
    ALTER MAPPING
    FOR hword, hword_part, word with unaccent, portuguese_stem;

    #Trigger para remover os acentos no FTS
    CREATE TRIGGER question_search_vector_trigger
    BEFORE INSERT OR UPDATE 
    ON public.question
    FOR EACH ROW
    EXECUTE PROCEDURE tsvector_update_trigger('search_vector', 'public.pt', 'question', 'answer');
    '''
    __searchable__ = ['question', 'answer']
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(800), index=False,
                         nullable=False, unique=True)
    _answer = db.Column('answer', db.Text, index=False,
                        nullable=True, unique=False)
    answer_approved = db.Column(db.Boolean, nullable=True, default=False)
    answer_approved_at = db.Column(db.DateTime(timezone=True))
    create_at = db.Column(db.DateTime(timezone=True), index=False, default=convert_datetime_to_local(datetime.utcnow()))
    create_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    update_at = db.Column(db.DateTime(timezone=True))
    update_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_approve_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_at = db.Column(db.DateTime(timezone=True))
    # tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=True)
    # topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    sub_topic_id = db.Column(
        db.Integer, db.ForeignKey('sub_topic.id'), nullable=True)
    question_network_id = db.Column(
        db.Integer, db.ForeignKey('network.id'), nullable=False)
    answer_network_id = db.Column(
        db.Integer, db.ForeignKey('network.id'), nullable=True)
    active = db.Column(db.Boolean, nullable=False)
    topics = db.relationship('Topic',
                             secondary=question_topic,
                             backref=db.backref('questions',
                                                lazy='dynamic', cascade='save-update', single_parent=True), lazy='dynamic')

    tags = db.relationship('Tag',
                           secondary=question_tag,
                           backref=db.backref('questions',
                                              lazy='dynamic', cascade='all, delete-orphan', single_parent=True,),
                           lazy='dynamic')
    search_vector = db.Column(TSVectorType(
        'question', 'answer', regconfig='public.pt', cache_ok=False))  # regconfig='public.pt'))

    view = db.relationship('QuestionView', cascade='all, delete-orphan',
                           single_parent=True, backref='question', lazy='dynamic')
    save = db.relationship('QuestionSave', cascade='all, delete-orphan',
                           single_parent=True, backref='question', lazy='dynamic')
    like = db.relationship('QuestionLike', cascade='all, delete-orphan',
                           single_parent=True, backref='question', lazy='dynamic')

    def __repr__(self):

        return f'<Question {self.question[:15] if not self.question  is None else None}>'

    @property
    def get_create_time_elapsed(self):
        return format_elapsed_time(self.create_at)

    @property
    def get_create_datetime(self):
        return format_datetime_local(self.create_at)

    @property
    def get_update_time_elapsed(self):
        return format_elapsed_time(self.update_at)

    @property
    def get_update_datetime(self):
        return format_datetime_local(self.update_at)

    @property
    def get_answer_time_elapsed(self):
        return format_elapsed_time(self.answer_at)

    @property
    def get_answer_datetime(self):
        return format_datetime_local(self.answer_at)

    @property
    def get_days_elapsed(self):
        return days_elapsed(self.create_at)

    @property
    def get_user_answer(self):
        if self.answered_by is None:
            return ''
        return self.answered_by.name

    # @property
    # def format_create_date(self):
    #     return self.create_at.strftime("%d/%m/%Y")
    # @property
    # def format_update_date(self):
    #     return self.update_at.strftime("%d/%m/%Y")
    # @property
    # def format_answer_date(self):
    #     return self.answer_at.strftime("%d/%m/%Y")

    @property
    def topic_name(self):
        return ', '.join([_.name for _ in self.topics])

    @property
    def sub_topic_name(self):
        return self.sub_topic.name

    @property
    def is_support(self):
        return 'Suporte' in [_.name for _ in self.topics]

    @hybrid_property
    def answer(self):
        return self._answer

    @property
    def is_approved_to(self):
        if self.answer_approved == True:
            return "Sim"
        return 'Não'

    @property
    def is_active(self):
        if self.active == True:
            return 'Sim'
        return 'Não'

    @property
    def process_answer(self):
        if self._answer != '' or self._answer != None:
            return process_value(self._answer, Question)
        return self._answer

    @hybrid_property
    def answer(self):
        return self._answer
        # return self._answer

    @answer.setter
    def answer(self, answer):
        self._answer = answer
        self.answer_approved = False
        if self.answer_user_id is None:
            raise Exception(
                '´answer_user_id´ deve ser informado para responder uma questão')


    @staticmethod
    def search(expression, pagination=False, per_page=1, page=1, resume=False, sub_topics: list = [], topics: list = []):
        # result = (db.session.query(Article, (func.strict_word_similarity(Article.text, 'principal')).label('similarity')).order_by(desc('similarity')))
        if not sub_topics:
            raise Exception('sub_topics não pode ser vazio')
        # if not topics:
        #     raise Exception('topics não pode ser vazio')
        if resume:
            result = (db.session.query(Question.question, (
                func.ts_rank_cd(
                    Question.search_vector(cache_ok=True),
                    func.plainto_tsquery(
                        'public.pt',
                        expression))).label(
                            'similarity')).filter((
                                func.ts_rank_cd(
                                    Question.search_vector,
                                    func.plainto_tsquery(
                                        'public.pt',
                                        expression))) > 0)  # .order_by(
                      # desc('similarity'))
                      )
        else:
            result = (db.session.query(Question, (
                func.ts_rank_cd(
                    Question.search_vector,
                    func.plainto_tsquery(
                        'public.pt',
                        expression))).label(
                            'similarity')).filter((
                                func.ts_rank_cd(
                                    Question.search_vector, func.plainto_tsquery('public.pt', expression))) > 0)  # .order_by(
                      # desc('similarity'))
                      )
        if not topics:
            result = result.filter(Question.sub_topic_id.in_(
                [_.id for _ in sub_topics]))
        else:
            result = result.filter(Question.sub_topic_id.in_(
                [_.id for _ in sub_topics])).join(Question.topics).filter(
                    Topic.id.in_([_.id for _ in topics]))
        if pagination:
            result = result.paginate(page=page, per_page=per_page)
        return result

    @property
    def resume(self):
        return self.question

    def was_updated(self):
        if self.update_at is None or self.update_user_id is None:
            return False
        return True

    def add_view(self, user_id, network_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        # qv = QuestionView.query.filter(QuestionView.question_id==self.id, QuestionView.user_id==user.id).first()
        qv = QuestionView()

        qv.question_id = self.id
        qv.user_id = user_id
        qv.network_id = network_id
        db.session.add(qv)

        # if qv == None:
        #     qv = QuestionView()
        #     qv.user_id = user_id
        #     qv.question_id = self.id
        #     qv.last_view = datetime.now()
        #     qv.count_view = 1
        #     db.session.add(qv)
        # else:
        #     qv.count_view += 1
        #     qv.last_view = datetime.now()
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            flash('Não foi possível atualizar a visualização', category='warning')
        return qv

    def add_like(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        ql = QuestionLike.query.filter(QuestionLike.question_id == self.id)
        like_user = ql.filter(QuestionLike.user_id == user_id).first()
        if not like_user is None:
            flash('Questão já curtida', category='info')
        ql = ql.first()
        if ql is None or like_user is None:
            ql = QuestionLike()
            ql.user_id = user.id
            ql.question_id = self.id
            ql.create_at = convert_datetime_to_local(datetime.utcnow())
            db.session.add(ql)
            try:
                db.session.commit()
            except Exception as e:
                app.logger.error(app.config.get(
                    '_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                flash('Não foi possível atualizar a visualização',
                      category='warning')
                return False
        return ql

    def remove_like(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        ql = QuestionLike.query.filter(
            QuestionLike.question_id == self.id, QuestionLike.user_id == user_id).first()
        if ql is None:
            raise Exception('Questão não foi curtida')
        db.session.delete(ql)
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            flash('Não foi possível atualizar a visualização', category='warning')
            return false
        return True

    def is_liked(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuários informado não existe')
        ql = QuestionLike.query.filter(
            QuestionLike.question_id == self.id, QuestionLike.user_id == user.id).first()
        if ql is None:
            return False
        return True

    def add_save(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        qs = QuestionSave.query.filter(QuestionSave.question_id == self.id)
        save_user = qs.filter(QuestionSave.user_id == user_id).first()
        if not save_user is None:
            flash('Questão já salva', category='info')
        qs = qs.first()
        if qs is None or save_user is None:
            qs = QuestionSave()
            qs.user_id = user.id
            qs.question_id = self.id
            qs.create_at = convert_datetime_to_local(datetime.utcnow())
            db.session.add(qs)
            try:
                db.session.commit()

            except Exception as e:
                app.logger.error(app.config.get(
                    '_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                db.session.rollback()
                flash('Não foi possível atualizar a visualização',
                      category='warning')
                return False
        return qs

    def remove_save(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        qs = QuestionSave.query.filter(
            QuestionSave.question_id == self.id, QuestionSave.user_id == user_id).first()
        if qs is None:
            raise Exception('Questão não foi curtida')
        db.session.delete(qs)
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            flash('Não foi possível atualizar a visualização', category='warning')
            return false
        return True

    def is_saved(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuários informado não existe')
        qs = QuestionSave.query.filter(
            QuestionSave.question_id == self.id, QuestionSave.user_id == user.id).first()
        if qs is None:
            return False
        return True

    @property
    def views(self):
        count_views = db.session.query(func.count(QuestionView.id)).filter(
            QuestionView.question_id == self.id).scalar()
        return 0 if count_views is None else count_views

    @property
    def likes(self):
        count_likes = db.session.query(func.sum(QuestionLike.question_id)).filter(
            QuestionLike.question_id == self.id).scalar()
        return 0 if count_likes is None else count_likes

    @property
    def was_approved(self):
        return self.answer_approved == True

    @property
    def was_answered(self):
        return self._answer != None

    @property
    def was_answered_to(self):
        if self.answer != None:
            return 'Sim'
        return 'Não'

    @staticmethod
    def most_viewed(limit=5, topic: Topic = None):
        try:
            if topic is None:
                return []
            rs = db.session.query(Question, func.count(QuestionView.id).label('views')).join(
                Question.view).join(Question.topics).group_by(Question).order_by(text('views DESC')).filter(Question.answer != None, Question.answer_approved == True, Topic.id == topic.id).limit(limit).all()
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return []
        return [x[0] for x in rs if x != None]

    @staticmethod
    def most_liked(limit=5, classification=True, topic: Topic = None):
        try:
            if topic is None:
                return []
            rs = db.session.query(Question, func.count(QuestionLike.id).label('likes')).join(
                Question.like).join(Question.topics).group_by(Question).order_by(text('likes DESC')).filter(Question.answer != None, Question.answer_approved == True, Topic.id == topic.id).limit(limit).all()
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return []
        if classification:
            return [x for x in rs if x != None]
        return [x[0] for x in rs if x != None]

    @staticmethod
    def likes_by_user(user_id, topic: Topic = None):
        if topic is None:
            return None
        user = User.query.filter(User.id == user_id).first_or_404()
        rs = db.session.query(Question).join(
            QuestionLike.question).filter(
                QuestionLike.user_id == user.id
                ).join(Question.topics
                ).filter(Topic.id == topic.id
                ).order_by(Question.create_at.desc())
        return rs

    @staticmethod
    def saves_by_user(user_id, topic: Topic = None):
        if topic is None:
            return None
        user = User.query.filter(User.id == user_id).first_or_404()
        rs = db.session.query(Question).filter(Question.topic_id == topic.id).join(
            QuestionSave.question).filter(
                QuestionSave.user_id == user.id).order_by(Question.create_at.desc())
        return rs

    def get_body_html(self, resume=False, size=1500):
        html_classes = {'table': 'table table-bordered',
                        'img': 'img img-fluid'}
        if resume:
            l_text = list(filter(lambda x: x not in [
                          '', ' ', '\t'], self.process_answer.split('\n')))
            # text = get_list_max_len(l_text, 256)
            return Markup(process_html(markdown('\n'.join(l_text), extras={"tables": None, "html-classes": html_classes, 'target-blank-links':True}))).striptags()[0:size] + '...'
            # return Markup(process_html(markdown(text))).striptags()

        return Markup(markdown(self.process_answer, extras={"tables": None, "html-classes": html_classes, 'target-blank-links':True}))

    def to_dict(self):
        return {'id': self.id,
                'question': self.get_body_html(),
                'create_time_elapsed': self.get_create_time_elapsed,
                'create_at': self.get_create_datetime,
                'author': self.author.name,
                'update_at': self.get_update_time_elapsed if self.was_updated() else None,
                'updater': self.updater.name if self.was_updated() else None,
                'answer': self.get_body_html() if self.was_answered else None,
                'answered_by': self.answered_by.name if self.was_answered else None,
                'answered_at': self.get_answer_time_elapsed if self.was_answered else None,
                'topics': [x.name for x in self.topics], #self.topic.name if not self.topic is None else None,
                'tags': [x.name for x in self.tags],
                'views': self.views
                }

    @staticmethod
    def query_by_month_year(year: int, month: int):
        return Question.query.filter(extract('year', Question.create_at) == year, extract('month', Question.create_at) == month)

    @staticmethod
    def query_by_year(year: int):
        return Question.query.filter(extract('year', Question.create_at) == year)

    @staticmethod
    def query_by_date(date: date):
        return Question.query.filter(cast(Question.create_at, Date) == date)

    @staticmethod
    def query_by_interval(start: date, end: date):
        return Question.query.filter(cast(Question.create_at, Date) == start, cast(Question.create_at, Date) == end)

    @staticmethod
    def count_by_topic(topic: str = ''):
        if topic == '':
            raise ValueError('topic não pode ser vazio')
        return Question.query.filter(Topic.name == topic).count()


class QuestionView(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,  db.ForeignKey(
        'user.id', onupdate="CASCADE", ondelete="CASCADE"))
    question_id = db.Column(db.Integer, db.ForeignKey(
        'question.id'), nullable=False)
    datetime = db.Column(db.DateTime(timezone=True), index=True, default=convert_datetime_to_local(datetime.utcnow()))
    network_id = db.Column(db.Integer, db.ForeignKey(
        'network.id'), nullable=False)

    # last_view = db.Column(db.DateTime, index=True, nullable=False)
    # count_view = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f'<Question View id: {self.question_id} by {self.user_id}>'

    def views_by_question(self, question_id: int):
        return db.session.query(func.count(self.id)).filter(self.question_id == question_id).scalar()

    def views_by_user(self, user_id: int):
        return db.session.query(func.count(self.id)).filter(self.user_id == user_id).scalar()

    @staticmethod
    def query_by_month_year(year: int, month: int):
        return QuestionView.query.filter(extract('year', QuestionView.datetime) == year, extract('month', QuestionView.datetime) == month)

    @staticmethod
    def query_by_year(year: int):
        return QuestionView.query.filter(extract('year', QuestionView.datetime) == year)

    @staticmethod
    def query_by_date(date: date):
        return QuestionView.query.filter(cast(QuestionView.datetime, Date) == date)

    @staticmethod
    def query_by_interval(start: date, end: date):
        return QuestionView.query.filter(cast(QuestionView.datetime, Date) == start, cast(QuestionView.datetime, Date) == end)


class QuestionLike(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey(
        'question.id'), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=convert_datetime_to_local(datetime.utcnow()))
    # user_like = db.relationship()

    def __repr__(self):
        return f'<Question Like id: {self.question_id} by {self.user_id}>'

    def likes_by_user(self, question_id: int):
        return self.query.filter(self.question_id == question_id).count()

    def likes_by_user(self, user_id: int):
        return self.query.filter(self.question_id == user_id).count()


class QuestionSave(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey(
        'question.id'), nullable=False)
    create_at = db.Column(db.DateTime, nullable=False, default=convert_datetime_to_local(datetime.utcnow()))

    def __repr__(self):
        return f'<Question Like id: {self.question_id} by {self.user_id}>'

    def saves_by_user(self, question_id: int):
        return self.query.filter(self.question_id == question_id).count()

    def saves_by_user(self, user_id: int):
        return self.query.filter(self.question_id == user_id).count()


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction = db.Column(db.String(10), unique=False, nullable=False)
    parameter = db.Column(db.String, nullable=True)
    option = db.Column(db.String)
    description = db.Column(db.String)
    datetime = db.Column(db.DateTime(timezone=True), nullable=False, default=convert_datetime_to_local(datetime.utcnow()))
    created_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<{self.transaction}>'


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
