# from sqlalchemy import func
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
from os.path import isfile

from sqlalchemy_searchable import make_searchable

from app.core.db import db
from app.utils.kernel import (
    convert_datetime_to_local,
    format_elapsed_time,
    get_list_max_len,
    only_letters,
    format_datetime_local,
    days_elapsed,
    process_value,
)
from app.utils.html import process_html
from app.models.security import User

transaction_topic = db.Table(
    "transaction_topic",
    db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id")),
    db.Column("topic_id", db.Integer, db.ForeignKey("topic.id")),
)
transaction_sub_topic = db.Table(
    "transaction_sub_topic",
    db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id")),
    db.Column("topic_sub_id", db.Integer, db.ForeignKey("sub_topic.id")),
)

class Transaction(db.Model):
    __searchable__ = ["transaction"]
    id = db.Column(db.Integer, primary_key=True)
    transaction = db.Column(db.String(4), unique=True, nullable=False)
    parameter_id = db.Column(db.ForeignKey('transaction_parameter.id'), nullable=False)
    type_id = db.Column(db.ForeignKey('transaction_type.id'), nullable=False)
    description = db.Column(db.String)
    create_at = db.Column(
        db.DateTime(timezone=True), index=False, default=convert_datetime_to_local
    )
    created_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    update_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    sub_topics = db.relationship(
        "SubTopic",
        secondary=transaction_sub_topic,
        backref=db.backref(
            "transactions", lazy="dynamic", cascade="save-update", single_parent=True
        ),
        lazy="dynamic",
    )
    topics = db.relationship(
        "Topic",
        secondary=transaction_topic,
        backref=db.backref(
            "transactions", lazy="dynamic", cascade="save-update", single_parent=True
        ),
        lazy="dynamic",
    )
    options = db.relationship('TransactionOption', backref='transaction', lazy='dynamic')
    screens = db.relationship('TransactionScreen', backref='transaction', lazy='dynamic')
    

    def __repr__(self):
        return f"<{self.transaction}>"


class TransactionParameter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32), index=True, nullable=False, unique=True)

class TransactionOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(64), index=True, nullable=False)
    description = db.Column(db.Text, index=True, nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)

class TransactionScreen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    screen_sequence = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.Text, nullable=False, unique=True)
    file_path = db.Column(db.Text, nullable=False, unique=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)

    def check_file(self) -> bool:
        if self.file_path is None or self.file_path == '':
            raise Exception('file_path deve ser um caminho válido')
        if isfile(self.file_path):
            return True
        return False
    

class TransactionType(db.Model):
    '''Incluir o tipo de transação Pesquisa ou Transação'''
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, nullable=False, unique=True)
    transactions = db.relationship('Transaction', backref='type', lazy='dynamic')