from flask import current_app as app, abort, flash
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
from datetime import datetime

from app.core.db import db
from app.utils.kernel import convert_datetime_to_local, format_elapsed_time
from app.models.security import User

class QuestionSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    count_access = db.Column(db.Integer, default=1)
    last_search = db.Column(db.DateTime, default=convert_datetime_to_local)
    first_search = db.Column(db.DateTime, default=convert_datetime_to_local)

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(256), nullable=False, unique=True)
    # count_search = db.Column(db.Integer, default=1)
    # search_date = db.Column(db.DateTime, default=convert_datetime_to_local)
    # last_search = db.Column(db.DateTime, default=convert_datetime_to_local)
    # question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    dates = db.relationship('SearchDateTime', backref='search', lazy='dynamic', cascade='all, delete-orphan')
    def __repr__(self):
        return f'<Search {self.text[0:10]}>'
   
    def add_search(self, user_id : int = None):
        # self.count_search += 1
        sdt = SearchDateTime()
        if not user_id is None:
            user = User.query.filter(User.id == user_id).first_or_404()
            if not user is None:
                sdt.search_user_id = user.id

        sdt.search_id = self.id
        sdt.search_datetime = convert_datetime_to_local()
        db.session.add(sdt)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return abort(500)
    def count_search(self):
        return db.session.query(func.count(SearchDateTime.id)).filter(SearchDateTime.search_id == self.id).scalar()
    

class SearchDateTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'), nullable=False)
    search_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    search_datetime = db.Column(db.DateTime, default=convert_datetime_to_local)
    