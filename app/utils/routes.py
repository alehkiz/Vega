from flask import current_app as app, request, abort, g, redirect, url_for
from flask_security import current_user
from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.routing import RequestRedirect
from app.models.app import Page, Visit
from app.models.security import User
from app.models.app import Network
from app.core.db import db
from functools import wraps

def counter(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # print(args)
        # print(kwargs)
        # print(request.url_rule.rule)
        if current_user.is_authenticated:
            user = current_user
        else:
            user = User.query.filter(User.id == app.config.get('USER_ANON_ID')).first()
            if user is None:
                app.logger.error('Usuário anonimo não encontrado')
                return abort(500)
        # print(g.get('topic_id'))
        if g.get('topic_id') is None:
            return redirect(url_for("main.select_access"))
        page = Page.query.filter(Page.endpoint == request.endpoint).first()
        if not hasattr(g, 'ip_id'):
            ip = Network.query.filter(Network.ip == request.remote_addr).first()
            if ip is None:
                ip = Network()
                ip.ip = request.remote_addr
                db.session.add(ip)
                try:
                    db.session.commit()
                    # 
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
                    app.logger.error(e)
                    return abort(500)
            g.ip_id=ip.id
        if page is None:
            page = Page()
            page.endpoint = request.endpoint
            page.route = request.url_rule.rule.split('<')[0]
            db.session.add(page)
        try:
            db.session.commit()
            page.add_view(user.id, g.ip_id, g.get('topic_id'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get('_ERRORS').get('DB_COMMIT_ERROR'))
            app.logger.error(e)
            return abort(500)
        return f(*args, **kwargs)
    return decorated_function


def route_exists(path, method='GET', query_args=None):
    """Check if the PATH exists for the application.

    Args:
        path (_type_): _description_
        method (str, optional): _description_. Defaults to 'GET'.
        query_args (_type_, optional): _description_. Defaults to None.
    Returns:
        True: Exists
        False: Not found
    """

    adapter = app.create_url_adapter(None)

    if adapter is None:
        raise Exception('Configure a SERVER_NAME for app')
    
    try:
        adapter.match(path, method, query_args)
    except (MethodNotAllowed, NotFound):
        return False
    return True