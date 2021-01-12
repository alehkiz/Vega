from flask_security import Security
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask.cli import with_appcontext
from flask_login import LoginManager

from app.blueprints import register_blueprints
from app.core.db import db, user_datastore

security = Security()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please login to access this page'
csrf = CSRFProtect()

def init(app):
    security.init_app(app, datastore=user_datastore, register_blueprint=False)
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    csrf.init_app(app)
    login.init_app(app)
    login.session_protection = 'strong'
    
    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    @with_appcontext
    def make_shell_context():
        app.config['SERVER_NAME'] = 'localhost'
        ctx = app.test_request_context()
        ctx.push()
        return dict(db=db, app=app, user=User)
    register_blueprints(app)
    return app