from datetime import datetime
from app.core.db import db
from app.models.wiki import Question
from app.utils.kernel import convert_datetime_to_local, format_datetime_local, process_value
from markdown2 import markdown
from flask import Markup
from app.utils.html import process_html


class QuestionHistory(db.Model):
    """
    Modelo para armazenar o histórico de modificações de `Question.
    """

    __searchable__ = ["question", "answer"]
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    question = db.Column(db.String(900), index=False, nullable=False)
    answer = db.Column(db.Text, index=False, nullable=True, unique=False)
    answer_approved = db.Column(db.Boolean, nullable=True, default=False)
    answer_approved_at = db.Column(db.DateTime(timezone=True))
    history_at = db.Column(
        db.DateTime(timezone=True), index=False, default=convert_datetime_to_local
    )
    update_at = db.Column(db.DateTime(timezone=True), default=convert_datetime_to_local)
    update_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    answer_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    add_history_user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    answer_approve_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    answer_at = db.Column(db.DateTime(timezone=True))
    answer_network_id = db.Column(
        db.Integer, db.ForeignKey("network.id"), nullable=True
    )
    active = db.Column(db.Boolean, nullable=False)
    network_id = db.Column(db.Integer, db.ForeignKey("network.id"), nullable=True)

    def __repr__(self) -> str:
        return f"<Question {self.question_id}>"

    def get_from_question(self, question: Question, add_history_user_id: int = None) -> None:
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
        self.update_user_id = question.update_user_id
        self.answer_user_id = question.answer_user_id
        if add_history_user_id != None and isinstance(add_history_user_id, int):
            self.add_history_user_id = add_history_user_id
        self.answer_approve_user_id = question.answer_approve_user_id
        self.answer_network_id = question.answer_network_id

    @property
    def get_history_at(self):
        return format_datetime_local(self.history_at)

    def get_body_html(self, resume=False, size=1500):
        html_classes = {"table": "table table-bordered", "img": "img img-fluid"}
        if resume:
            l_text = list(
                filter(
                    lambda x: x not in ["", " ", "\t"], self.process_answer.split("\n")
                )
            )
            return (
                Markup(
                    process_html(
                        markdown(
                            "\n".join(l_text),
                            extras={
                                "tables": None,
                                "html-classes": html_classes,
                                "target-blank-links": True,
                            },
                        )
                    )
                ).striptags()[0:size]
                + "..."
            )

        return Markup(
            markdown(
                self.process_answer,
                extras={
                    "tables": None,
                    "html-classes": html_classes,
                    "target-blank-links": True,
                },
            )
        )

    @property
    def process_answer(self):
        if self.answer != "" or self.answer != None:
            return process_value(self.answer, Question)
        return self.answer
