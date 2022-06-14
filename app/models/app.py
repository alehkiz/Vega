# from sqlalchemy import func
from enum import unique
from os import stat
from flask import Markup, escape, current_app as app, abort, flash
from flask_login import login_required
from sqlalchemy import func, text, Index, cast, desc, extract, Date, asc
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date, datetime
from sqlalchemy.orm import backref
from sqlalchemy.dialects.postgresql import INET
from app.utils.kernel import convert_datetime_to_local

from app.core.db import db

from app.models.security import User
from app.utils.kernel import format_date_local, format_datetime_local

file_topic = db.Table('file_pdf_topic',
                        db.Column('file_id', db.Integer, db.ForeignKey('file_pdf.id')),
                        db.Column('topic_id', db.Integer, db.ForeignKey('topic.id')))


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String, unique=True, nullable=False)
    route = db.Column(db.String, unique=True, nullable=False)
    visit = db.relationship('Visit', cascade='all, delete-orphan',
                            single_parent=True, backref='page', lazy='dynamic')

    def add_view(self, user_id, network_id, topic_id):
        
        
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        visit = Visit()
        visit.page_id = self.id
        visit.user_id = user.id
        visit.network_id = network_id
        visit.topic_id = topic_id
        visit.datetime = convert_datetime_to_local(datetime.utcnow())
        db.session.add(visit)
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            flash('Não foi possível atualizar a visualização', category='warning')
        return visit


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=True)
    datetime = db.Column(db.DateTime(timezone=True), nullable=False, default=convert_datetime_to_local(datetime.utcnow()))
    network_id = db.Column(db.Integer, db.ForeignKey('network.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)

    @staticmethod
    def query_by_month_year(year: int, month: int):
        return Visit.query.filter(extract('year', Visit.datetime) == year, extract('month', Visit.datetime) == month)

    @staticmethod
    def query_by_year(year: int):
        return Visit.query.filter(extract('year', Visit.datetime) == year)

    @staticmethod
    def query_by_date(date: date):
        return Visit.query.filter(cast(Visit.datetime, Date) == date)

    @staticmethod
    def query_by_interval(start: date, end: date):
        return Visit.query.filter(cast(Visit.datetime, Date) == start, cast(Visit.datetime, Date) == end)

    @staticmethod
    def total_by_date(start: str, end: str):
        start = datetime.strptime(start, '%d-%m-%Y')
        end = datetime.strptime(end, '%d-%m-%Y')
        # timedelta = (end - start).days
        # if timedelta > 60:
        #     raise Exception('Intervalo de datas maior que 60 dias')
        return db.session.query(
                func.count(Visit.id).label('total'),
                cast(Visit.datetime, Date).label('date')
            ).filter(
               Visit.datetime.between(start, end)
            ).group_by('date').order_by(asc('date'))

    @staticmethod
    def total_by_year_month(year: int, month=None):
        if year < 2020:
            raise Exception('Ano deve ser maior de 2020')

        if month is None:
            return db.session.query(
                func.count(Visit.id).label('total'),
                cast(Visit.datetime, Date).label('date')
            ).filter(
                extract('year', Visit.datetime) == year
            ).group_by('date')
        if month < 1 or month > 12:
            raise Exception('Mês inválido')
       
        return db.session.query(
            func.count(Visit.id).label('total'),
            cast(Visit.datetime, Date).label('date')
        ).filter(
            extract('year', Visit.datetime) == year,
            extract('month', Visit.datetime) == month
        ).group_by('date')
    @staticmethod
    def visits_by_ip(ips : list = None):
        """Return a query object with a lista of network in ips and the count of access

        Args:
            ips (list, optional): IPs. Defaults to None.

        Returns:
            BaseQuery: A BaseQuery with number of access for each IP
        """        
        if list is None:
            query = db.session.query(Network, func.count(Network.id).label('views')).join(Visit.network).group_by(Network)
        else:
            query = db.session.query(Network, func.count(Network.id).label('views')).join(Visit.network).filter(Network.ip.in_(ips)).group_by(Network)
        return query
class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(INET, nullable=False)
    create_at = db.Column(db.DateTime(timezone=True), default=convert_datetime_to_local(datetime.utcnow()))
    created_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # first_access = db.Column(db.DateTime, nullable=False, default=datetime.now())
    question_created_ip = db.relationship('Question', backref='question_created_network', lazy='dynamic', foreign_keys='[Question.question_network_id]')
    answer_created_ip = db.relationship('Question', backref='answer_created_network', lazy='dynamic', foreign_keys='[Question.answer_network_id]')
    questions_views = db.relationship('QuestionView', cascade='all, delete-orphan', single_parent=True, backref='network', lazy='dynamic')
    created_user = db.relationship('User', backref='created_network', lazy='dynamic', foreign_keys='[User.created_network_id]')
    last_login_user = db.relationship('User', backref='last_login_network', lazy='dynamic', foreign_keys='[User.last_login_network_id]')
    current_login_user = db.relationship('User', backref='current_login_network', lazy='dynamic', foreign_keys='[User.current_login_network_id]')
    confirmed_user = db.relationship('User', backref='confirmed_network', lazy='dynamic', foreign_keys='[User.confirmed_network_id]')
    notifiers = db.relationship('Notifier', backref='network', lazy='dynamic', single_parent=True)
    visits = db.relationship('Visit', backref='network', lazy='dynamic', single_parent=True)
    # created_citizen = db.relationship('Citizen', backref='created_network', lazy='dynamic', foreign_keys='[Citizen.created_network_id]')


class FilePDF(db.Model):
    __tablename__ = 'file_pdf'
    id = db.Column(db.Integer, primary_key=True)
    uploaded_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime(timezone=True), default=convert_datetime_to_local(datetime.utcnow()))
    mimetype = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.Text, nullable=False, unique=True)
    approved_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    active = db.Column(db.Boolean, nullable=False)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    path = db.Column(db.Text, nullable=False, unique=True)
    size = db.Column(db.Float, nullable=False)
    reference_date = db.Column(db.Date, nullable=True)
    title = db.Column(db.Text, nullable=False)
    update_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("file_pdf_type.id"), nullable=False)
    sub_topic_id = db.Column(db.Integer, db.ForeignKey('sub_topic.id'), nullable=True)
    topics = db.relationship('Topic', secondary=file_topic, 
                                backref=db.backref('files', lazy='dynamic', cascade='save-update', single_parent=True), lazy='dynamic')
    view = db.relationship('FileView', cascade='save-update',
                        single_parent=True, backref='file', lazy='dynamic')

    @property
    def get_create_datetime(self):
        return format_datetime_local(self.uploaded_at)
    
    @property
    def get_reference_date(self):
        return format_date_local(self.reference_date)

    @property
    def was_approved(self):
        if self.approved == True:
            return "Sim" 
        return 'Não'
    
    @property
    def type_name(self):
        if self.type != None:
            return self.type.name
        return None
    @property
    def topic_name(self):
        return ', '.join([_.name for _ in self.topics])
    def add_view(self, user_id, network_id, topic_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        # qv = QuestionView.query.filter(QuestionView.question_id==self.id, QuestionView.user_id==user.id).first()
        fv = FileView()

        fv.file_pdf_id = self.id
        fv.user_id = user_id
        fv.network_id = network_id
        fv.topic_id = topic_id
        db.session.add(fv)
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            flash('Não foi possível atualizar a visualização', category='warning')
        return fv
        
class FilePDFType(db.Model):
    __tablename__ = 'file_pdf_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    create_at = db.Column(db.DateTime(timezone=True), default=convert_datetime_to_local(datetime.utcnow()))
    create_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    active = db.Column(db.Boolean, default=False)
    url_route = db.Column(db.Text)
    login_required = db.Column(db.Boolean, default=False)
    files = db.relationship('FilePDF', backref='type', lazy='dynamic')

class FileView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))
    file_pdf_id = db.Column(db.Integer, db.ForeignKey('file_pdf.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True)
    datetime = db.Column(db.DateTime(timezone=True), index=True, default=convert_datetime_to_local(datetime.utcnow()))
    network_id = db.Column(db.Integer, db.ForeignKey(
        'network.id'), nullable=False)
    def __repr__(self):
        return f'<File View id: {self.file_pdf_id} by {self.id}>'

    def views_by_file_pdf(self, file_pdf_id: int):
        return db.session.query(func.count(self.id)).filter(self.file_pdf_id == file_pdf_id).scalar()
    
    def views_by_user(self, user_id:int):
        return db.session.query(func.count(self.id)).filter(self.user_id == user_id).scalar()
    
    @staticmethod
    def query_by_month_year(year: int, month: int):
        return FileView.query.filter(extract('year', FileView.datetime) == year, extract('month', FileView.datetime) == month)

    @staticmethod
    def query_by_year(year: int):
        return FileView.query.filter(extract('year', FileView.datetime) == year)

    @staticmethod
    def query_by_date(date: date):
        return FileView.query.filter(cast(FileView.datetime, Date) == date)

    @staticmethod
    def query_by_interval(start: date, end: date):
        return FileView.query.filter(cast(FileView.datetime, Date) == start, cast(FileView.datetime, Date) == end)