from flask import Flask
from config.config import config
from logging import INFO
from app.core.configure import init
from app.core.db import init_db_command


def create_app(mode='production'):
    app = Flask(__name__)
    app.config.from_object(config[mode])
    init(app)
    app.cli.add_command(init_db_command)
    app.logger.setLevel(INFO)
    app.logger.info('Vega start')
    return app
