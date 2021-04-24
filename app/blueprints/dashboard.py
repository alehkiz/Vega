from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, g, abort, request, current_app as app
from flask_security import login_required, current_user
from datetime import datetime
from app.core.db import db
from app.models.wiki import Article, Question, Tag, Topic
from app.models.app import Page, Visit
from app.models.security import User
from app.utils.routes import counter
from app.utils.dashboard import Dashboard
from app.models.search import Search
bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/index')
def index():
    # print(app.index())
    dashboard = Dashboard()
    dashboard.start()
    return render_template('dashboard/dashboard.html', dash=dashboard)
    # return redirect('/dashboard/')