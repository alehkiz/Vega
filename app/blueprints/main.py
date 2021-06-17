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
)
from flask_security import login_required, current_user
from datetime import datetime

from app.core.db import db
from app.models.wiki import Article, Question, Tag, Topic
from app.models.app import Network, Page, Visit
from app.models.security import User
from app.forms.question import QuestionSearchForm
from app.forms.search import SearchForm
from app.utils.routes import counter

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
        current_user.last_seen = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error("Não foi possível salvar ultima visualização do usuário")
            app.logger.error(e)
            return abort(500)

    if not session.get("AccessType", False):

        current_rule = request.url_rule
        if not current_rule is None and current_rule.endpoint not in [
            "main.select_access",
            "static",
        ]:
            
            return redirect(url_for("main.select_access"))
    else:          
        if not Topic.query.filter(Topic.name == session.get("AccessType", False)).first() is None:
            g.selected_access = session.get("AccessType", False)
        else:
            session.pop('AccessType')
            resp = make_response(redirect(url_for("question.index")))
            resp.set_cookie(key="AccessType", value="", expires=0)
            flash("Ocorreu um erro", category="danger")
            return resp
    
    if session.get("AccessType", False):
        g.tags = Tag.query.all()

        g.topic = Topic.query.filter(Topic.selectable == True, Topic.name == g.selected_access).first()
        g.questions_most_viewed = Question.most_viewed(app.config.get("ITEMS_PER_PAGE", 5), g.topic)
        g.questions_most_recent = (
            Question.query.order_by(Question.create_at.desc())
            .filter(Question.answer_approved == True, Question.topic_id==g.topic.id)
            .limit(app.config.get("ITEMS_PER_PAGE", 5))
            .all()
        )
        g.questions_most_liked = Question.most_liked(
            app.config.get("ITEMS_PER_PAGE", 5), topic=g.topic, classification=False
        )
    ip = Network.query.filter(Network.ip == request.remote_addr).first()
    if ip is None:
        ip = Network()
        ip.ip = request.remote_addr
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


@bp.route("/")
@bp.route("/index")
@counter
def index():
    if current_user.is_authenticated and (
        current_user.is_admin or current_user.is_editor or current_user.is_support
    ):
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
                        "card_style": "bg-danger bg-gradient text-dark",
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
                        "bt_name": "Visualisar",
                        "bt_route": url_for(
                            "question.topic", name=_.name, type="aprovada"
                        ),
                        "card_style": "bg-primary bg-gradient text-dark",
                    },
                ],
            }
            for _ in Topic.query.all()
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

        tags = Tag.query.filter(Question.topic_id == topic.id).all()

        tags_question = [{"name": 'Marcações', "values": [{
            'title': _.name,
            'count': _.questions.filter(Question.answer_approved == True).count(),
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
    obj_topic = Topic.query.filter(Topic.name.ilike(topic.lower())).first_or_404()
    response = make_response(redirect(url_for("main.index")))
    response.set_cookie(key="AccessType", value=obj_topic.name)
    session["AccessType"] = obj_topic.name
    return response
    # print(obj_topic)
    # return topic
    # if request.cookies.get('AccessType', False):
    #     flash('Módulo selecionado')
    #     return redirect(url_for('question.index'))
    # response = Response()
    # response.set_cookie(key='AccessType', value='ValuePage')


@bp.route("/access/<string:topic>")
def selected_access(topic=None):
    if topic is None:
        return redirect(url_for("main.select_access"))

    obj_topic = Topic.query.filter(Topic.name.ilike(topic.lower())).first_or_404()
    response = make_response(redirect(url_for("main.index")))
    response.set_cookie(key="AccessType", value=obj_topic.name)
    return response


@bp.route("/search")
def search():
    # print(g.tags)
    page = request.args.get("page", 1, type=int)
    if g.search_form.validate():
        search = Search.query.filter(Search.text.ilike(g.search_form.q.data)).first()
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
                app.logger.error(app.config.get("_ERRORS").get("DB_COMMIT_ERROR"))
                app.logger.error(e)
                return abort(500)
        else:
            if current_user.is_authenticated:
                search.add_search(current_user.id)
            else:
                search.add_search()
        paginate = Question.search(
            g.search_form.q.data, page=page, per_page=app.config.get("ITEMS_PER_PAGE")
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
