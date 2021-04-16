from flask_security import Security
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask.cli import with_appcontext
from flask_login import LoginManager
from logging.handlers import RotatingFileHandler
import logging
from flask_talisman import Talisman
# from elasticsearch import Elasticsearch

from os.path import exists
from os import mkdir


from app.blueprints import register_blueprints
from app.core.db import db, user_datastore
from app.models.security import User, Role
from app.models.wiki import Article, Topic, Tag, ArticleView, Question, QuestionLike, QuestionSave, QuestionView
from app.models.search import Search, SearchDateTime

security = Security()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please login to access this page'
csrf = CSRFProtect()
talisman = Talisman()
SELF = "'self'"

csp = {
    'default-src': ['\'self\'',
                    'https://cdn.jsdelivr.net/codemirror.spell-checker/',
                    'https://maxcdn.bootstrapcdn.com/font-awesome/'
    ],
    'script-src': ['\'self\'', 
                    'https://maxcdn.bootstrapcdn.com/font-awesome/',
                    'https://cdn.jsdelivr.net/codemirror.spell-checker/'
    ],
    'style-src': ["'self'",
                    "https: 'unsafe-inline'",
                    'https://maxcdn.bootstrapcdn.com/font-awesome/',
                    'https://cdn.jsdelivr.net/codemirror.spell-checker/'
    ],
    'style-src-elem': "'unsafe-inline'",
    'img-src': ["'self'", 
                '*',
                'data:;'],
    'media-src': '*'
}
def init(app):
    security.init_app(app, datastore=user_datastore, register_blueprint=False)
    db.init_app(app)
    db.configure_mappers()
    migrate.init_app(app, db, render_as_batch=True)
    csrf.init_app(app)
    login.init_app(app)
    login.session_protection = 'strong'
    talisman.init_app(app,
                        force_https_permanent=True,
                        content_security_policy=csp,
                        content_security_policy_nonce_in=['script-src','style-src','style-src-elem','script-src-elem','default-src']
    )
    ### SEARCH

    # app.elasticsearch = Elasticsearch(app.config['ELASTICSEARCH_URL']) if app.config['ELASTICSEARCH_URL'] else None


    @app.shell_context_processor
    @with_appcontext
    def make_shell_context():
        app.config['SERVER_NAME'] = 'localhost'
        ctx = app.test_request_context()
        ctx.push()
        return dict(db=db, app=app, User=User, Role=Role, Article=Article, Tag=Tag, Topic=Topic, 
            ArticleView=ArticleView, 
            Question=Question,
            QuestionLike=QuestionLike, 
            QuestionSave=QuestionSave, 
            QuestionView=QuestionView, 
            Search=Search,
            SearchDateTime = SearchDateTime
            )
    register_blueprints(app)

    # logger
    if not exists('logs'):
        mkdir('logs')
    file_handler = RotatingFileHandler(
        'logs/erros.log', maxBytes=1024000, backupCount=100)
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    

    @login.user_loader
    def load_user(id):
        try:
            user = User.query.get(int(id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return None
        return user
    return app
