from flask import Flask

from app.core.configure import init

def create_app(config='dev'):

    app = Flask(__name__)
    init(app)
    return app