from flask_security import Security
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

security = Security()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()