from os.path import abspath, dirname, join
from os import environ

import logging

import app


class BaseConfig(object):
    PROJECT_NAME = 'Vega'
    SECRET_KEY = environ.get(
        'SERVER_KEY')# or b'Y\xde\xba\xd7q\xa1\x87#\xb9\x10\xddA\xe4x\xb1\xadg\xc3\x16\xa15\xa1T\x9b\xff\xd5\x851`\xf5\xd7['
    APP_DIR = abspath(dirname(app.__file__))
    BASE_DIR = abspath(join(APP_DIR, '..'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    SECURITY_CHANGEABLE = True
    BLUEPRINTS_DIR = join(APP_DIR, 'blueprints')
    LOG_DIR = join(BASE_DIR, r'logs')
    DEV_DB = join(APP_DIR, r'db//db.db')
    SESSION_COOKIE_SECURE = True
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

    BABEL_DEFAULT_LOCALE = 'pt_BR'

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
            },
            "create_at": {
                'name' : 'criado em',
                'attr' : 'get_create_datetime'
            },
            'answer':{
                'name' : 'Respondida?',
                'attr' : 'was_answered_to'
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
        },
        'sub_topic' :{
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

    # ACCESS_TYPE = {
    #     'citizen' : 'Cidadão',
    #     'backoffice' : 'Retaguarda'
    # }

    # ELASTICSEARCH_URL = 'http://localhost:9200'



class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BaseConfig.DEV_DB}'
    SQLALCHEMY_DATABASE_URI = f'postgresql://{BaseConfig._SQLALCHEMY_DATABASE_USERNAME}:{BaseConfig._SQLALCHEMY_DATABASE_PASSWORD}@{BaseConfig._SQLALCHEMY_DATABASE_HOST}/{BaseConfig._SQLALCHEMY_DATABASE_NAME}'
    
    ENV = 'dev'


class TestConfig(BaseConfig):
    TESTING = True


class ProductionConfig(BaseConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLALCHEMY_DATABASE_URI = f'postgresql://{BaseConfig._SQLALCHEMY_DATABASE_USERNAME}:{BaseConfig._SQLALCHEMY_DATABASE_PASSWORD}@{BaseConfig._SQLALCHEMY_DATABASE_HOST}/{BaseConfig._SQLALCHEMY_DATABASE_NAME}'
    SQLALCHEMY_DATABASE_URI = f'postgresql://khtknuvbaeavvq:98b557036b61944f2912ccc6aa07b0c907352da55603ce611bb9b744da9398fa@ec2-23-23-128-222.compute-1.amazonaws.com:5432/dtf9faocttt57'
# 
config = {'development': DevelopmentConfig,
          'production': ProductionConfig}
