from os.path import abspath, dirname, join
from os import environ

import app

class BaseConfig(object):
    PROJECT_NAME = 'Vega'
    SECRET_KEY = environ.get('SERVER_KEY') or 'ZdsQPA7z8fyFHV_aqB8ZrY-yTvAODWKV4qKOp-vzkcFZUsWVvuwd4GpdjfoV2uITNj8B6S_3bMyc68ciolUxOCFKN2tCJ5RhDJcI_Xm0I0b1xyCzoS7Kc03YURCYaoSQ2xZKxDMrYl1OvGREYjaUGRx4aJ6lNUH1qZm4mONjAHE'
    APP_DIR = abspath(dirname(app.__file__))
    BASE_DIR = abspath(join(APP_DIR, '..'))

    BLUEPRINTS_DIR = join(APP_DIR, 'blueprints')
    LOG_DIR = join(BASE_DIR, r'logs')
    DEV_DB = join(APP_DIR, r'db\db.db')

    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = SECRET_KEY
    SECURITY_LOGIN_URL = 'auth.login'
    SECURITY_TRACKABLE = True
    SECURITY_POST_LOGIN_VIEW = 'auth.login'
    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_MSG_UNAUTHORIZED = ('Você não tem permissão para acessar essa página', 'danger')
    SECURITY_MSG_LOGIN = ('É necessário se logar para acessar essa página', 'info')

    _SQLALCHEMY_DATABASE_NAME = PROJECT_NAME
    _SQLALCHEMY_DATABASE_HOST = 'localhost'
    _SQLALCHEMY_DATABASE_USERNAME = 'root'
    _SQLALCHEMY_DATABASE_PASSWORD = environ.get('DB_PASS') or None


    _ERRORS = {'DB_COMMIT_ERROR': 'Não foi possível atualizar o banco de dados'}


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BaseConfig.DEV_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'dev'
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    SECURITY_CHANGEABLE = True

class TestConfig(BaseConfig):
    TESTING = True


class ProductionConfig(BaseConfig):

    SQLALCHEMY_DATABASE_URI = f'postgresql://{BaseConfig._SQLALCHEMY_DATABASE_USERNAME}:{BaseConfig._SQLALCHEMY_DATABASE_PASSWORD}@{BaseConfig._SQLALCHEMY_DATABASE_HOST}/{BaseConfig._SQLALCHEMY_DATABASE_NAME}'


config = {'development': DevelopmentConfig}