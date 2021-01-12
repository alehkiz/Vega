from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemyUserDatastore

db = SQLAlchemy(session_options={'autoflush':False})

from app.models.security import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)