from flask_security import UserMixin, RoleMixin
from flask_security.utils import hash_password, verify_password
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.db import db

from datetime import datetime


roles_users = db.Table('roles_users',
                            db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                            db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class User(UserMixin, db.Model()):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, nullable=False, unique=True)
    name = db.Column(db.String(512), index=True, nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    _password = db.Column(db.String(512), nullable=False)
    about_me = db.Column(db.String(512))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(128), nullable=True)
    active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_ip = db.Column(db.String(255), nullable=False)
    last_login_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_ip = db.Column(db.String(255), nullable=True)
    current_login_at = db.Column(db.DateTime, nullable=True)
    current_login_ip = db.Column(db.String(255), nullable=True)
    confirmed_ip = db.Column(db.String(255), nullable=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, nullable=True, default=0)


    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = hash_password(password)

    def check_password(self, password):
        return verify_password(password, self.password)





    def __repr__(self):
        return f'<User {self.username}>'

class Role(RoleMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    leve = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Role {self.name}>'