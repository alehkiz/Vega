from app.models.search import Search
from flask import (
    current_app as app,
    Blueprint,
    render_template,
    url_for,
    redirect,
    flash,
    json,
    Markup,
    g,
    abort,
    request,
    current_app as app,
    Response,
    make_response,
    session,
    jsonify,
)
from flask_security import login_required, current_user
from datetime import datetime
from sqlalchemy import func

from app.core.db import db
from app.models.wiki import Article, Question, QuestionView, Tag, Topic
from app.models.app import Network, Page, Visit
from app.models.security import User
from app.forms.question import QuestionSearchForm
from app.forms.search import SearchForm
from app.utils.routes import counter
# from app.core.extensions import cache

# from app.dashboard import dash
from app.utils.dashboard import Dashboard

bp = Blueprint("main", __name__, url_prefix="/")


@bp.before_app_first_request
def before_first_request():
    ...


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
    g.question_search_form = SearchForm()
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(
                "Não foi possível salvar ultima visualização do usuário")
            app.logger.error(e)
            return abort(500)

    if not session.get("AccessType", False):
        current_rule = request.url_rule
        if Topic.query.filter(Topic.selectable == True).count() > 1:
            if not current_rule is None and current_rule.endpoint not in [
                "main.select_access",
                "static",
            ]:
                return redirect(url_for("main.select_access"))
        else:
            topic = Topic.query.filter(Topic.selectable == True).first()
            response = make_response(redirect(url_for(current_rule.endpoint)))
            response.set_cookie(key="AccessType", value=topic.name)
            session["AccessType"] = topic.name
            g.selected_access = topic.name
            return response

    else:
        selected_topic = Topic.query.filter(
            Topic.name == session.get("AccessType", False)).first()
        if not selected_topic is None:
            if not selected_topic.active:
                session.pop('AccessType')
                resp = make_response(redirect(url_for("question.index")))
                resp.set_cookie(key="AccessType", value="", expires=0)
                flash("Ocorreu um erro", category="danger")
                return resp
            else:
                g.selected_access = session.get("AccessType", False)
        else:
            session.pop('AccessType')
            resp = make_response(redirect(url_for("question.index")))
            resp.set_cookie(key="AccessType", value="", expires=0)
            flash("Ocorreu um erro", category="danger")
            return resp
    if session.get("AccessType", False):
        g.tags = Tag.query.all()
        g.topic = Topic.query.filter(
            Topic.selectable == True, Topic.name == g.selected_access).first()
        if not g.topic is None:

            g.questions_most_viewed = Question.most_viewed(
                app.config.get("ITEMS_PER_PAGE", 5), g.topic)
            g.questions_most_recent = db.session.query(Question).filter(Question.answer_approved == True).join(
                Topic, Question.topics).filter(Topic.id == g.topic.id).order_by(Question.create_at.desc()).limit(app.config.get("ITEMS_PER_PAGE", 5)).all()
            # (
            #     Question.query.order_by(Question.create_at.desc())
            #     .filter(Question.answer_approved == True, Question.topic_id == g.topic.id)
            #     .limit(app.config.get("ITEMS_PER_PAGE", 5))
            #     .all()
            # )
            g.questions_most_liked = Question.most_liked(
                app.config.get("ITEMS_PER_PAGE", 5), topic=g.topic, classification=False
            )
    _ip = request.access_route[0] or request.remote_addr
    ip = Network.query.filter(Network.ip == _ip).first()
    if ip is None:
        ip = Network()
        ip.ip = _ip
        db.session.add(ip)

        try:
            db.session.commit()
            g.ip_id = ip.id
        except Exception as e:
            db.session.rollback()
            app.logger.error(app.config.get("_ERRORS").get("DB_COMMIT_ERROR"))
            app.logger.error(e)
            return abort(500)
    else:
        g.ip_id = ip.id


# @bp.before_request
# @counter
# def before_request():
#     pass

@bp.teardown_request
def teardow_request_test(exception):
    try:
        db.session.close()
    except Exception as e:
        app.logger.error(app.config.get("_ERRORS").get("DB_COMMIT_ERROR"))
        app.logger.error(e)
        # return abort(500)


@bp.teardown_app_request
def teardown_request(exception):
    try:
        db.session.close()
    except Exception as e:
        app.logger.error(app.config.get("_ERRORS").get("DB_COMMIT_ERROR"))
        app.logger.error(e)


@bp.route("/")
@bp.route("/index")
@counter
def index():
    if current_user.is_authenticated and current_user.has_support:
        topics = [
            {
                "id": _.id,
                "name": _.name,
                "values": [
                    {
                        "title": "Perguntas pendentes",
                        "count": _.questions.filter(Question.answer == None).count(),
                        "bt_name": "Responder",
                        "bt_route": url_for("admin.questions", topic=_.name),
                        "card_style": "bg-danger bg-gradient text-white",
                    },
                    {
                        "title": "Para aprovação",
                        "count": _.questions.filter(
                            Question.answer != None, Question.answer_approved == False
                        ).count(),
                        "bt_name": "Aprovar",
                        "bt_route": url_for("admin.to_approve", topic=_.name),
                        "card_style": "bg-warning bg-gradient text-dark",
                    },
                    {
                        "title": "Aprovadas",
                        "count": _.questions.filter(
                            Question.answer_approved == True
                        ).count(),
                        "bt_name": "Acessar",
                        "bt_route": url_for(
                            "question.topic", name=_.name, type="aprovada"
                        ),
                        "card_style": "bg-primary bg-gradient text-white",
                    },
                ],
            }
            for _ in Topic.query.filter(Topic.selectable == True).all()
        ]
        return render_template("index.html", topics=topics)
    else:
        topic = Topic.query.filter(
            Topic.name.ilike(session.get("AccessType", False))
        ).first_or_404()

        topic_question = [
            {
                "id": topic.id,
                "name": topic.name,
                "values": [
                    {
                        "title": "Aprovadas",
                        "count": topic.questions.filter(
                            Question.answer_approved == True
                        ).count(),
                        "bt_name": "Visualizar",
                        "bt_route": url_for(
                            "question.topic", name=topic.name, type="aprovada"
                        ),
                        "card_style": "bg-primary bg-gradient text-dark",
                    }
                ],
            }
        ]

        tags = db.session.query(Tag).join(Question.tags)

        tags.group_by(Tag).order_by(func.count(Question.id).desc())

        tags_question = [{"name": 'Marcações', "values": [{
            'title': _.name,
            'count': _.questions_approved(g.topic).count(),
            'bt_name': 'Visualizar',
            'bt_route': url_for('question.tag', name=_.name, type='aprovada'),
            'card_style': 'bg-success br.gradient text-dark'
        } for _ in tags]}]

        return render_template("index.html", topics=topic_question, tags=tags_question)
    page = request.args.get("page", 1, type=int)
    if not session.get("AccessType", False):
        return redirect(url_for("main.index"))
    questions = Question.query.filter(Question.answer_approved == True)
    # TODO completar
    paginate = questions.order_by(Question.create_at.desc()).paginate(
        per_page=app.config.get("QUESTION_PER_PAGE"), page=page
    )
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None


@bp.route("/select_access/")
@bp.route("/select_access/<string:topic>")
def select_access(topic=None):
    if topic is None:
        topics = Topic.query.filter(Topic.selectable == True).all()
        return render_template("select_access.html", topics=topics)
    obj_topic = Topic.query.filter(
        Topic.name.ilike(topic.lower())).first_or_404()
    response = make_response(redirect(url_for("main.index")))
    response.set_cookie(key="AccessType", value=obj_topic.name)
    session["AccessType"] = obj_topic.name
    return response


@bp.route("/access/<string:topic>")
def selected_access(topic=None):
    if topic is None:
        return redirect(url_for("main.select_access"))

    obj_topic = Topic.query.filter(
        Topic.name.ilike(topic.lower())).first_or_404()
    response = make_response(redirect(url_for("main.index")))
    response.set_cookie(key="AccessType", value=obj_topic.name)
    return response


@bp.route("/search")
@counter
def search():
    page = request.args.get("page", 1, type=int)
    if g.search_form.validate():
        search = Search.query.filter(
            Search.text.ilike(g.search_form.q.data)).first()
        if search is None:
            search = Search()
            search.text = g.search_form.q.data
            search.add_search(current_user.id)
            db.session.add(search)
            try:
                db.session.commit()
                if current_user.is_authenticated:
                    search.add_search(current_user.id)
                else:
                    search.add_search()
            except Exception as e:
                db.session.rollback()
                app.logger.error(app.config.get(
                    "_ERRORS").get("DB_COMMIT_ERROR"))
                app.logger.error(e)
                return abort(500)
        else:
            if current_user.is_authenticated:
                search.add_search(current_user.id)
            else:
                search.add_search()
        paginate = Question.search(
            g.search_form.q.data, page=page, per_page=app.config.get(
                "ITEMS_PER_PAGE")
        )
    # article = Article.search(g.search_form.q.data, False, resume=True)
    # result = question.union_all(article).paginate(page=page, per_page=app.config.get('ITEMS_PER_PAGE'))
    iter_pages = list(paginate.iter_pages())
    first_page = iter_pages[0] if len(iter_pages) >= 1 else None
    last_page = paginate.pages if paginate.pages > 0 else None
    # result_question = Question.search()
    return render_template(
        "search.html",
        cls_question=Question,
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        url_arguments={"q": g.search_form.q.data},
    )


@bp.route('/autocomplete/', methods=['GET'])
def autocomplete():
    search = request.args.get("q", '', type=str)
    if search == '':
        jsonify(result=[])

    # return a query orded by most viewed question, where question has search and question is approved, active and answered

    if current_user.is_authenticated:
        result = db.session.query(Question, func.count(QuestionView.id).label('views')).outerjoin(QuestionView).filter(
            Question.answer != '', Question.answer_approved == True, Question.active == True).filter(func.to_tsvector('public.pt', Question.question).op(
                '@@')(func.plainto_tsquery('public.pt', search))).group_by(Question).order_by(func.count(QuestionView.id).desc())

    else:
        result = db.session.query(Question, func.count(QuestionView.id).label('views')).outerjoin(QuestionView).filter(
            Question.answer != '', Question.answer_approved == True, Question.active == True).join(Question.topics).filter(Topic.id == g.topic.id).filter(func.to_tsvector('public.pt', Question.question).op(
                '@@')(func.plainto_tsquery('public.pt', search))).group_by(Question).order_by(func.count(QuestionView.id).desc())
        # result = result.filter(func.to_tsvector('public.pt', Question.question).op(
    # '@@')(func.plainto_tsquery('public.pt', search)))
    # result = [_[0] for _ in result.limit(10).all()]
    result = [{'link': url_for('question.view', id=_[0].id),
               'label': _[0].question}
              for _ in result.limit(10).all()]
    return jsonify(result=result)


# db.session.query(Question).filter(func.to_tsvector('public.pt', Question.question).op('@@')(func.plainto_tsquery('public.pt', search))).join(QuestionView).filter(func.count(QuestionView.id).label('total')).all()
