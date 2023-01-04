from datetime import datetime
from app.core.db import db
from app.models.wiki import Question
from app.utils.kernel import convert_datetime_to_local


class QuestionHistory(db.Model):
    '''
    Modelo para armazenar o histórico de modificações de `Question.
    '''
    __searchable__ = ['question', 'answer']
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(
        db.Integer, db.ForeignKey('question.id'), nullable=False)
    question = db.Column(db.String(900), index=False,
                         nullable=False, unique=True)
    answer = db.Column(db.Text, index=False,
                       nullable=True, unique=False)
    answer_approved = db.Column(db.Boolean, nullable=True, default=False)
    answer_approved_at = db.Column(db.DateTime(timezone=True))
    history_at = db.Column(db.DateTime(timezone=True), index=False, default=convert_datetime_to_local)
    # create_user_id = db.Column(
    #     db.Integer, db.ForeignKey('user.id'), nullable=False)
    update_at = db.Column(db.DateTime(timezone=True), default=convert_datetime_to_local)
    update_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_approve_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer_at = db.Column(db.DateTime(timezone=True))
    answer_network_id = db.Column(
        db.Integer, db.ForeignKey('network.id'), nullable=True)
    active = db.Column(db.Boolean, nullable=False)

    def __repr__(self) -> str:
        return f'<Question {self.question_id}>'


    def get_from_question(self, question: Question) -> None:
        if not isinstance(question, Question):
            raise Exception(f"question não é uma instância de Question")
        self.question_id = question.id
        self.question = question.question
        self.answer = question.answer
        self.answer_approved = question.answer_approved
        self.answer_approved_at = question.answer_approved_at
        self.answer_approve_user_id = question.answer_approve_user_id
        self.answer_at = question.answer_at
        self.answer_network_id = question.answer_network_id
        self.active = question.active


    