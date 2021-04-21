# from sqlalchemy import func
from enum import unique
from os import stat
from flask import Markup, escape, current_app as app, abort, flash
from sqlalchemy import func, text, Index, cast, desc, extract, Date
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date, datetime
from sqlalchemy.orm import backref


from app.core.db import db
from app.models.security import User


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String, unique=True, nullable=False)
    route = db.Column(db.String, unique=True, nullable=False)
    visit = db.relationship('Visit', cascade='all, delete-orphan',
                            single_parent=True, backref='page', lazy='dynamic')

    def add_view(self, user_id):
        user = User.query.filter(User.id == user_id).first()
        if user is None:
            raise Exception('Usuário informado não existe')
        visit = Visit()
        visit.page_id = self.id
        visit.user_id = user.id
        db.session.add(visit)
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            db.session.rollback()
            flash('Não foi possível atualizar a visualização')
        return visit


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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
    def total_by_date(year: int, month=None):
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
            extract('month') == month
        ).group_by('date')
