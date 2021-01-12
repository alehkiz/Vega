from os.path import abspath, dirname, join

import app

class BaseConfig(object):
    SECRET_KEY = 'ZdsQPA7z8fyFHV_aqB8ZrY-yTvAODWKV4qKOp-vzkcFZUsWVvuwd4GpdjfoV2uITNj8B6S_3bMyc68ciolUxOCFKN2tCJ5RhDJcI_Xm0I0b1xyCzoS7Kc03YURCYaoSQ2xZKxDMrYl1OvGREYjaUGRx4aJ6lNUH1qZm4mONjAHE'
    BASEDIR = abspath(dirname(app.__file__))
    DEV_DB = join(BASEDIR, r'db\db.db')
    SECRET_KEY = 'RUqhRwcoW3-VaETTaasSDD@3SDwW__W---w0w9wvn4RYo1sZVKLnz70_ptEUrXmEUXs'
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = SECRET_KEY
    SECURITY_LOGIN_URL = 'auth.login'

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BaseConfig.DEV_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

config = {'development': DevelopmentConfig}