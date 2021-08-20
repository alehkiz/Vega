# from sqlalchemy import func
from enum import unique
from os import stat
from flask import Markup, escape, current_app as app, abort, flash
from sqlalchemy import func, text, Index, cast, desc, extract, Date, asc
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date, datetime
from sqlalchemy.orm import backref
from sqlalchemy.dialects.postgresql import INET


from app.core.db import db

from app.models.security import User

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String, unique=True, nullable=False)
    route = db.Column(db.String, unique=True, nullable=False)
    visit = db.relationship('Visit', cascade='all, delete-orphan',
                            single_parent=True, backref='page', lazy='dynamic')

    def add_view(self, user_id, network_id):
        
        
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        visit = Visit()
        visit.page_id = self.id
        visit.user_id = user.id
        visit.network_id = network_id
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
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    network_id = db.Column(db.Integer, db.ForeignKey('network.id'), nullable=False)

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

class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(INET, nullable=False)
    create_at = db.Column(db.DateTime, default=datetime.utcnow)
    # first_access = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    question_created_ip = db.relationship('Question', backref='question_created_network', lazy='dynamic', foreign_keys='[Question.question_network_id]')
    answer_created_ip = db.relationship('Question', backref='answer_created_network', lazy='dynamic', foreign_keys='[Question.answer_network_id]')
    questions_views = db.relationship('QuestionView', cascade='all, delete-orphan', single_parent=True, backref='network', lazy='dynamic')
    created_user = db.relationship('User', backref='created_network', lazy='dynamic', foreign_keys='[User.created_network_id]')
    last_login_user = db.relationship('User', backref='last_login_network', lazy='dynamic', foreign_keys='[User.last_login_network_id]')
    current_login_user = db.relationship('User', backref='current_login_network', lazy='dynamic', foreign_keys='[User.current_login_network_id]')
    confirmed_user = db.relationship('User', backref='confirmed_network', lazy='dynamic', foreign_keys='[User.confirmed_network_id]')
    # created_citizen = db.relationship('Citizen', backref='created_network', lazy='dynamic', foreign_keys='[Citizen.created_network_id]')