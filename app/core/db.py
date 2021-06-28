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
    click.echo('Banco de dados inicializado...')
    from app.models.wiki import Topic
    from app.models.security import User
    atendimento = Topic.query.filter(Topic.name == 'Atendimento').first()
    if atendimento is None:
        atendimento = Topic()
        atendimento.name = 'Atendimento'
        atendimento.format_name = 'Atendimento'
        atendimento.selectable = True
        db.session.add(atendimento)
    retaguarda = Topic.query.filter(Topic.name == 'Retaguarda').first()
    if retaguarda is None:
        retaguarda = Topic()
        retaguarda.name = 'Retaguarda'
        retaguarda.format_name = 'Retaguarda'
        retaguarda.selectable = True
        db.session.add(retaguarda)
    
    db.session.commit()

    click.echo('Topicos iniciados')

    anon = User()
    anon.username = 'ANON'
    anon.name = 'ANON'
    anon.email = 'anon@localhost'
    anon.created_ip = '0.0.0.0'
    anon._password = '123'
    anon.temp_password = True
