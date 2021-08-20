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
    db.drop_all()
    db.create_all()
    click.echo('Banco de dados inicializado...')
    from app.models.wiki import Topic
    from app.models.security import User
    from app.models.app import Network
    network = Network.query.filter(Network.ip == '0.0.0.0').first()
    if network is None:
        network = Network()
        network.ip = '0.0.0.0'
        db.session.add(network)
        db.session.commit()
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
    suporte = Topic.query.filter(Topic.name == 'Suporte').first()
    if suporte is None:
        suporte = Topic()
        suporte.name = 'Suporte'
        suporte.format_name = 'Suporte'
        suporte.selectable = False
        db.session.add(suporte)    
    db.session.commit()

    click.echo('Topicos iniciados.')

    anon = User.query.filter(User.username == 'ANON').first()
    
    if anon is None:
        anon = User()
        anon.id = 4
        anon.username = 'ANON'
        anon.name = 'ANON'
        anon.email = 'anon@localhost'
        anon.created_network_id = network.id
        anon._password = '123'
        anon.current_login_network_id = network.id
        anon.temp_password = True
        db.session.add(anon)
        db.session.commit()
        click.echo('Usuário anonimo adicionado')

    admin = User.query.filter(User.username == 'admin').first()
    if admin is None:
        admin = User()
        admin.username = 'admin'
        admin.name = 'admin'
        admin.email = 'admin@localhost'
        admin.created_network_id = network.id
        admin.current_login_network_id = network.id
        admin.password = 'Abc123'
        admin.active = True
        admin.temp_password = False
        db.session.add(admin)
        db.session.commit()
        click.echo('Administrador criado...')


    admin_role = Role()
    admin_role.level = 0
    admin_role.name = 'admin'
    admin_role.description = 'Administrator'

    man_user = Role()
    man_user.level = 1
    man_user.name = 'manager_user'
    man_user.description = 'Gerenciador de Usuários'

    man_cont = Role()
    man_cont.level = 2
    man_cont.name = 'manager_content'
    man_cont.description = 'Gerenciador de Conteúdo'

    aux_cont = Role()
    aux_cont.level = 3
    aux_cont.name = 'aux_content'
    aux_cont.description = 'Colaborador de Conteúdo'

    support_cont = Role()
    support_cont.level = 5
    support_cont.name = 'support'
    support_cont.description = 'Suporte'

    view_cont = Role()
    view_cont.level = 5
    view_cont.name = 'viewer_content'
    view_cont.description = 'Visualizador de Conteúdo'

    db.session.add(admin)
    db.session.add(man_user)
    db.session.add(man_cont)
    db.session.add(view_cont)
    db.session.add(support_cont)
    admin.roles.append(admin_role)

    db.session.commit()

    click.echo('Perfis criados.')