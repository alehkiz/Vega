from flask import current_app as app, request
from flask_security import current_user
from app.models.app import Page, Visit
from app.models.security import User
from app.models.app import Network
from app.core.db import db
from functools import wraps

def counter(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("dentro do decorator")
        if current_user.is_authenticated:
            user = current_user
        else:
            user = User.query.filter(User.id == app.config.get('USER_ANON_ID')).first()
            if user is None:
                app.logger.error('Usuário anonimo não encontrado')
                app.logger.error()
                abort(500)
        page = Page.query.filter(Page.endpoint == request.endpoint).first()
        ip = Network.query.filter(Network.ip == request.remote_addr).first()
        if ip is None:
            ip = Network()
            ip.ip = request.remote_addr
            db.session.add(ip)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                app.logger.error(e)
                return abort(500)
        if page is None:
            page = Page()
            page.endpoint = request.endpoint
            page.route = request.url_rule.rule.split('<')[0]
            db.session.add(page)
        try:
            db.session.commit()
            page.add_view(user.id, ip.id)
            # print('aqui')s
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return abort(500)
        return f(*args, **kwargs)
    return decorated_function