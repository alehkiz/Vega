from flask_caching import Cache
from flask_security import Security
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CsrfProtect
from flask_login import LoginManager

cache = Cache()
security = Security()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()