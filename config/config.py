from os.path import abspath, dirname, join
from os import environ

import logging
from re import M

import app


class BaseConfig(object):
    PROJECT_NAME = 'Vega'
    SITE_TITLE = environ.get('PROJECT_NAME') or 'AtenDetran'
    SECRET_KEY = environ.get(
        'SERVER_KEY')
    APP_DIR = abspath(dirname(app.__file__))
    BASE_DIR = abspath(join(APP_DIR, '..'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    SECURITY_CHANGEABLE = True
    BLUEPRINTS_DIR = join(APP_DIR, 'blueprints')
    LOG_DIR = join(BASE_DIR, r'logs')
    # DEV_DB = join(APP_DIR, r'db//db.db')
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = environ.get('PASSWORD_SALT')
    SECURITY_LOGIN_URL = 'auth.login'
    SECURITY_TRACKABLE = True
    SECURITY_POST_LOGIN_VIEW = 'auth.login'
    SECURITY_CONFIRMABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_MSG_UNAUTHORIZED = (
        'Você não tem permissão para acessar essa página', 'danger')
    SECURITY_MSG_LOGIN = (
        'É necessário se logar para acessar essa página', 'info')

    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"options": "-c timezone=America/Sao_Paulo"}}

    BABEL_DEFAULT_LOCALE = 'pt_BR'

    _SQLALCHEMY_DATABASE_NAME = environ.get('DATABASE', False) or PROJECT_NAME.lower()
    _SQLALCHEMY_DATABASE_HOST = environ.get('DB_HOST')
    _SQLALCHEMY_DATABASE_USERNAME = environ.get('DB_USER')
    _SQLALCHEMY_DATABASE_PASSWORD = environ.get('DB_PASS')
    _SQLALCHEMY_DATABASE_PORT = environ.get('DB_PORT')

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
            'topics' : {
                'name' : 'Tópicos',
                'attr' : 'topic_name'
            },
            'sub_topics' :{
                'name' : 'Sub Tópico',
                'attr' : 'sub_topic_name'
            },
            'answered_by':{
                'name': 'Respondido por',
                'attr': 'get_user_answer'
            },
            "create_at": {
                'name' : 'criado em',
                'attr' : 'get_create_datetime'
            },
            'answer_at':{
                'name': 'Respondida em',
                'attr': 'get_answer_datetime'
            },
            'answer':{
                'name' : 'Respondida?',
                'attr' : 'was_answered_to'
            },
            'answer_approved':{
                'name' : 'Aprovada?',
                'attr' : 'is_approved_to'
            },
            'active':{
                'name': 'ativa',
                'attr' : 'is_active'
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
        'topics' :{
            'id' :{
                'name' : 'id',
                'attr' : None
            },
            'name': {
                'name' : 'Nome',
                'attr' : None
            },
            # 'user': {
            #     'name' : 'criado por',
            #     'attr': 'username'

            # }
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
        'notifier':{
            'id': {
                'name': 'id',
                'attr': None
            },
            'title': {
                'name': 'Titulo',
                'attr': None
            },
            'status_id': {
                'name': 'Status',
                'attr': 'status_name'
            },
            'priority_id': {
                'name': 'Prioridade',
                'attr': 'priority_name'
            },
            'topic_id': {
                'name': 'Topico',
                'attr': 'topics_name'
            },
            'sub_topic_id': {
                'name': 'Sub Topico',
                'attr': 'sub_topics_name'
            },
            'level_id': {
                'name': 'Level',
                'attr': 'level_translate_name'
            },
            'created_at':{
                'name': 'Criado em',
                'attr': 'get_formated_date'
            },
            'autoload':{
                'name': 'Carregamento Automático',
                'attr': 'get_autoload'
            }
        },
        'file_pdf':{
            'id':{
                'name': 'id',
                'attr': None
            },
            'title':{
                'name': 'title',
                'attr': None
            },
            'reference_date':{
                'name': 'Criado em',
                'attr': 'get_reference_date'
            },
            'approved': {
                'name': "Aprovado",
                'attr': 'was_approved'
            },
            'type': {
                'name': 'Tipo',
                'attr': 'type_name'
            },
            'topics' : {
                'name' : 'Tópicos',
                'attr' : 'topic_name'
            },
        },
        'file_pdf_type' :{
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
    }
    ROUTES_NAMES = {
        'user': {
            'add': 'user.view',
            'edit': 'user.edit',
            'remove': 'user.remove'
        },
    }
    USER_ANON_ID = 4
    UPLOAD_FOLDER = join(APP_DIR, 'upload')
    OLD_UPLOAD_FOLDER = join(UPLOAD_FOLDER, '_old')
    MAX_CONTENT_LENGTH = 31457280 #20MB
    UPLOAD_EXTENSIONS = ['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'xlsx', 'xls']

    MSG_PASSWORD_VALIDATE = '''Senha deve conter mais que 6 caracteres, pelo menos um número, pelo menos uma letra maiúscula e pelo menos uma letra minúscula'''

class DevelopmentConfig(BaseConfig):
    # SQLALCHEMY_DATABASE_URI = f'sqlite:///{BaseConfig.DEV_DB}'
    SQLALCHEMY_DATABASE_URI = f'postgresql://{BaseConfig._SQLALCHEMY_DATABASE_USERNAME}:{BaseConfig._SQLALCHEMY_DATABASE_PASSWORD}@{BaseConfig._SQLALCHEMY_DATABASE_HOST}:{BaseConfig._SQLALCHEMY_DATABASE_PORT}/{BaseConfig._SQLALCHEMY_DATABASE_NAME}'
    MODE = 'dev'
    ENV = 'dev'


class TestConfig(BaseConfig):
    TESTING = True
    MODE = 'test'


class ProductionConfig(BaseConfig):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f'postgresql://{BaseConfig._SQLALCHEMY_DATABASE_USERNAME}:{BaseConfig._SQLALCHEMY_DATABASE_PASSWORD}@{BaseConfig._SQLALCHEMY_DATABASE_HOST}:{BaseConfig._SQLALCHEMY_DATABASE_PORT}/{BaseConfig._SQLALCHEMY_DATABASE_NAME}'
    # SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or f'postgresql://khtknuvbaeavvq:98b557036b61944f2912ccc6aa07b0c907352da55603ce611bb9b744da9398fa@ec2-23-23-128-222.compute-1.amazonaws.com:5432/dtf9faocttt57'
    SESSION_COOKIE_SECURE = False
    MODE = 'prod'
# 
config = {'development': DevelopmentConfig,
          'production': ProductionConfig}
