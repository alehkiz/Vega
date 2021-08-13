from re import S
from app.models.security import User, Role
from app.models.app import Network
from app.core.db import db
from os import environ

def create():
    network = Network()
    network.ip = '0.0.0.0'
    db.session.add(network)
    db.session.commit()

    adm = User()
    adm.username = 'admin'
    adm.name = 'Administrador'
    adm.email = 'adm@localhost.loc'
    adm.password = environ.get('ADMIN_PASS', True) or Exception('ADMIN_PASS deve ser configurado no servidor.')
    adm.temp_password = False
    adm.active = True
    adm.created_network_id = network.id
    db.session.add(adm)
    db.session.commit()
