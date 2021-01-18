from flask_security import UserMixin, RoleMixin
from flask_security.utils import hash_password, verify_password
from sqlalchemy.ext.hybrid import hybrid_property


from app.core.db import db
from app.utils.kernel import validate_password

from datetime import datetime


roles_users = db.Table('roles_users',
                            db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                            db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, nullable=False, unique=True)
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
    articles = db.relationship('Article', backref='author', lazy='dynamic', foreign_keys='[Article.user_id]')
    articles_updated = db.relationship('Article', backref='updater', lazy='dynamic', foreign_keys='[Article.updated_user_id]')
    articles_viewed = db.relationship('ArticleView', cascade='all, delete-orphan', backref='user', single_parent=True, lazy='dynamic')
    roles = db.relationship('Role', 
                secondary=roles_users, 
                backref=db.backref('users', lazy='dynamic'), 
                lazy='dynamic')
    
    @property
    def is_admin(self):
        if any([role.is_admin for role in self.roles.all()]):
            return True
        return False
    @property
    def is_manager_user(self):
        if any([role.is_manager_user for role in self.roles.all()]):
            return True
        return False
    @property
    def is_manager_content(self):
        if any([role.is_manager_content for role in self.roles.all()]):
            return True
        return False
    
    @property
    def is_collab_content(self):
        if any([role.is_collab_content for role in self.roles.all()]):
            return True
        return False

    @property
    def is_viewer(self):
        if any([role.is_viewer for role in self.roles.all()]):
            return True
        return False
    
    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        _validate_password = validate_password(password)
        if _validate_password['ok']:
            self._password = hash_password(password)
        else:
            raise ValueError('Não foi possível validar a senha')

    def check_password(self, password):
        return verify_password(password, self.password)




    def __repr__(self):
        return f'<User {self.username}>'

class Role(RoleMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, unique=False, nullable=False)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)

    @property
    def is_admin(self):
        if self.level == 0:
            return True
        return False

    @property
    def is_manager_user(self):
        if self.level == 1:
            return True
        return False

    @property
    def is_manager_content(self):
        if self.level == 2:
            return True
        return False

    @property
    def is_collab_content(self):
        if self.level == 3:
            return True
        return False

    @property
    def is_viewer(self):
        if self.level == 4:
            return True
        return False

    def __repr__(self):
        return f'<Role {self.name}>'