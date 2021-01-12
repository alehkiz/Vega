from flask import Flask
from config.config import config

from app.core.configure import init

def create_app(mode='dev'):

    app = Flask(__name__)
    app.config.from_object(config[mode])
    init(app)
    return app