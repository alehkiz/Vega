from os.path import abspath, dirname, join
from os import environ

import logging

import app


class BaseConfig(object):
    PROJECT_NAME = 'Vega'
    SECRET_KEY = environ.get(
        'SERVER_KEY') or 'ZdsQPA7z8fyFHV_aqB8ZrY-yTvAODWKV4qKOp-vzkcFZUsWVvuwd4GpdjfoV2uITNj8B6S_3bMyc68ciolUxOCFKN2tCJ5RhDJcI_Xm0I0b1xyCzoS7Kc03YURCYaoSQ2xZKxDMrYl1OvGREYjaUGRx4aJ6lNUH1qZm4mONjAHE'
    APP_DIR = abspath(dirname(app.__file__))
    BASE_DIR = abspath(join(APP_DIR, '..'))

    BLUEPRINTS_DIR = join(APP_DIR, 'blueprints')
    LOG_DIR = join(BASE_DIR, r'logs')
    DEV_DB = join(APP_DIR, r'db//db.db')

    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = SECRET_KEY
    SECURITY_LOGIN_URL = 'auth.login'
    SECURITY_TRACKABLE = True
    SECURITY_POST_LOGIN_VIEW = 'auth.login'
    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_MSG_UNAUTHORIZED = (
        'Você não tem permissão para acessar essa página', 'danger')
    SECURITY_MSG_LOGIN = (
        'É necessário se logar para acessar essa página', 'info')

    _SQLALCHEMY_DATABASE_NAME = PROJECT_NAME.lower()
    _SQLALCHEMY_DATABASE_HOST = environ.get('DB_USER') or 'localhost'
    _SQLALCHEMY_DATABASE_USERNAME = environ.get('DB_USER') or 'alexandre'
    _SQLALCHEMY_DATABASE_PASSWORD = environ.get('DB_PASS') or 'contato'

    _ERRORS = {'DB_COMMIT_ERROR': 'Não foi possível atualizar o banco de dados'}

    DEFAULT_PASS = 'Abc123'

    ITEMS_PER_PAGE = 5
    QUESTIONS_PER_PAGE = 10
    TABLE_ITEMS_PER_PAGE = 15

    # Variável responsável pelo DE-PARA entre as colunas das tabelas
    TABULATE = {
        'article': {
            'id': {'name': 'id',
                   'attr': None},
            'title': {'name': 'titulo',
                      'attr': None},
            'description': {'name': 'descrição',
                            'attr': None},
            'text': {'name': 'texto',
                     'attr': 'get_text_resume'},
            'updadet_time_stamp': {'name': 'Criado em',
                                   'attr': 'format_create_date'}
        },
        'user': {
            "id": {"name": "id",
                   "attr": None
                   },
            "username": {
                "name": "username",
                "attr": None
            },
            "name": {
                "name": "name",
                "attr": None
            },
            "email": {
                "name": "email",
                "attr": None
            },
            "active": {
                "name": "ativo",
                "attr": 'format_active'
            },
            "created_at": {
                "name": "criado em",
                "attr": 'format_create_date'
            },
        },
        'question' : {
            'id' : {
                'name' : 'id',
                'attr': None
            },
            'question' : {
                'name' : 'Dúvida',
                'atrr' : None
            },
            'answer' : {
                'name' : 'Resposta',
                'attr' : None
            }

        },
        'tag' :{
            'id' :{
                'name' : 'id',
                'attr' : None
            },
            'name': {
                'name' : 'Nome',
                'attr' : None
            },
            'user': {
                'name' : 'criado por',
                'attr': 'username'

            }
        },
        'topic' :{
            'id' :{
                'name' : 'id',
                'attr' : None
            },
            'name': {
                'name' : 'Nome',
                'attr' : None
            },
            'user': {
                'name' : 'criado por',
                'attr': 'username'

            }
        }
    }
    ROUTES_NAMES = {
        'user': {
            'add': 'user.view',
            'edit': 'user.edit',
            'remove': 'user.remove'
        },
        # 'article':{
        #     'add': 'article.view',
        #     'edit': '.edit',
        #     'remove': '.remove'
        # }   
        # ,
        # 'article':{
        #     'add': '.add',
        #     'edit': '.edit',
        #     'remove': '.remove'
        # }
    }
    USER_ANON_ID = 4

    # ELASTICSEARCH_URL = 'http://localhost:9200'



class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BaseConfig.DEV_DB}'
    SQLALCHEMY_DATABASE_URI = f'postgresql://{BaseConfig._SQLALCHEMY_DATABASE_USERNAME}:{BaseConfig._SQLALCHEMY_DATABASE_PASSWORD}@{BaseConfig._SQLALCHEMY_DATABASE_HOST}/{BaseConfig._SQLALCHEMY_DATABASE_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = 'dev'
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    SECURITY_CHANGEABLE = True


class TestConfig(BaseConfig):
    TESTING = True


class ProductionConfig(BaseConfig):

    SQLALCHEMY_DATABASE_URI = f'postgresql://{BaseConfig._SQLALCHEMY_DATABASE_USERNAME}:{BaseConfig._SQLALCHEMY_DATABASE_PASSWORD}@{BaseConfig._SQLALCHEMY_DATABASE_HOST}/{BaseConfig._SQLALCHEMY_DATABASE_NAME}'


config = {'development': DevelopmentConfig,
          'production': ProductionConfig}
