from flask import current_app as app, abort, flash
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

from app.core.db import db
from app.utils.kernel import format_elapsed_time

class QuestionSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    search_id = db.Column(db.Integer, db.ForeignKey('search.id'))
    count_access = db.Column(db.Integer, default=1)
    last_search = db.Column(db.DateTime, default=datetime.utcnow)
    first_search = db.Column(db.DateTime, default=datetime.utcnow)

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(256), nullable=False, unique=True)
    count_search = db.Column(db.Integer, default=1)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_search = db.Column(db.DateTime, default=datetime.utcnow)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))


    def __repr__(self):
        return f'<Search {self.text[0:10]}>'
        
    
    def add_count(self):
        self.count_search += 1
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return abort(500)


