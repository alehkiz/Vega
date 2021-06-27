from flask_sqlalchemy import SQLAlchemy
from flask_security import SQLAlchemyUserDatastore
import click
from flask.cli import with_appcontext
# from flask_security import SQLAlchemySessionUserDatastore

db = SQLAlchemy(session_options={'autoflush':False})

from app.models.security import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# user_datastore = SQLAlchemySessionUserDatastore(db, User, Role)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()
    click.echo('Initialized the database.')