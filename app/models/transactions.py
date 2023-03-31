# from sqlalchemy import func
from typing import Optional
from flask import Markup, escape, current_app as app, abort, flash, url_for
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
    format_datetime_local
)
from app.utils.html import process_html
from app.models.security import User
from app.utils.others import limit_chars

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

transaction_parameter = db.Table(
    "transaction_parameter",
    db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id")),
    db.Column("parameter_id", db.Integer, db.ForeignKey("parameter.id")),
)

transaction_finalities = db.Table(
    "transaction_finalities",
    db.Column("transaction_id", db.Integer, db.ForeignKey("transaction.id")),
    db.Column("finality_id", db.Integer, db.ForeignKey("transaction_finality.id")),
)

class Transaction(db.Model):
    __searchable__ = ["transaction"]
    id = db.Column(db.Integer, primary_key=True)
    transaction = db.Column(db.String(4), unique=True, nullable=False)
    type_id = db.Column(db.ForeignKey('transaction_type.id'), nullable=False)
    description = db.Column(db.String)
    create_at = db.Column(db.DateTime(timezone=True), index=False, default=convert_datetime_to_local)
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

    finalities = db.relationship(
        "TransactionFinality",
        secondary=transaction_finalities,
        backref=db.backref(
            "transactions", lazy="dynamic", cascade="save-update", single_parent=True
        ),
        lazy="dynamic",
    )

    options = db.relationship('TransactionOption', backref='transaction', lazy='dynamic')
    screens = db.relationship('TransactionScreen', backref='transaction', lazy='dynamic')
    parameters = db.relationship(
        "Parameter",
        secondary=transaction_parameter,
        backref=db.backref(
            "transactions", lazy="dynamic", cascade="save-update", single_parent=True
        ),
        lazy="dynamic",
    )
    @property
    def topics_name(self) -> str:
        return ','.join([x.name for x in self.topics])
    
    @property
    def sub_topics_name(self) -> str:
        return ','.join([x.name for x in self.sub_topics])
    
    @property
    def type_name(self) -> str:
        return self.type.name
    
    @property
    def get_formated_date(self):
        return format_datetime_local(self.create_at)

    def get_body_html(self, resume=False, size=1500):
        html_classes = {'table': 'table table-bordered',
                        'img': 'img img-fluid'}
        if resume:
            l_text = list(filter(lambda x: x not in [
                          '', ' ', '\t'], self.description.split('\n')))
            # text = get_list_max_len(l_text, 256)
            return Markup(process_html(markdown('\n'.join(l_text),
                                                extras={"tables": None, "html-classes": html_classes, 'target-blank-links': True}))).striptags()[0:size] + '...'
            # return Markup(process_html(markdown(text))).striptags()

        return Markup(markdown(self.description, extras={"tables": None, "html-classes": html_classes, 'target-blank-links': True}))


    @property
    def to_dict(self):
        return {
            'id': self.id,
            'transaction': self.transaction,
            'description': limit_chars(self.get_body_html(), 50),
            'finalities' : ', '.join([x.name for x in self.finalities]),
            'topics' : ', '.join([x.name for x in self.topics]),
            'subtopics': ', '.join([x.name for x in self.sub_topics]),
            'options': ', '.join([x.option for x in self.options]),
            'screens': Markup('<br>'.join([x.img_tag() for x in self.screens])),
            'url': Markup(f'<a href=url_for("api.notification", id=self.id)>Link</a>'),

        }

    @property
    def to_dict_detail(self):
        return {
            'id': self.id,
            'transaction': self.transaction,
            'content': self.get_body_html(),
            'status': self.status_name,
            'level': self.level_bootstrap_name,
            'priority': self.priority_name,
            'priority_order': self.priority_order,
            'created_elapsed_time': self.get_create_time_elapsed,
            'subtopic': '' if self.sub_topics.first() is None else self.sub_topics.first().name,
            'view_link': Markup(f'<a class="view text-decoration-none" href="{url_for("notifier.view", id=self.id)}" data-bs-toggle="tooltip" title="Visualizar"><i class="fas fa-search-plus"></i></a>'),
            'edit_link': Markup(f'<a class="edit text-decoration-none" id="edit_notification" href="{url_for("notifier.edit", id=self.id)}" data-bs-toggle="tooltip" title="Editar"><i class="fas fa-edit"></i></a>')
        }



    def __repr__(self):
        return f"<{self.transaction}>"


class Parameter(db.Model):
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
    transaction_option_id = db.Column(db.Integer, db.ForeignKey('transaction_option.id'), nullable=True)
    # active = db.Column(db.Float, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    uploaded_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    update_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    uploaded_at = db.Column(
        db.DateTime(timezone=True), default=convert_datetime_to_local
    )
    mimetype = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, index=True, nullable=False)
    size = db.Column(db.Integer)

    
    def check_file(self) -> bool:
        if self.file_path is None or self.file_path == '':
            raise Exception('file_path deve ser um caminho válido')
        if isfile(self.file_path):
            return True
        return False
    
    def img_tag(self, width:int=200, height:Optional[int]=None) -> Markup:
        url = url_for('transactions.screen', id=self.id)
        print(url)
        return f'<img src="{url}" width="{width}", heigth="{height}">'


class TransactionType(db.Model):
    '''Incluir o tipo de transação Pesquisa ou Transação'''
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, nullable=False, unique=True)
    transactions = db.relationship('Transaction', backref='type', lazy='dynamic')

class TransactionFinality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    # transactions = db.relationship('Transaction', backref='type', lazy='dynamic')
