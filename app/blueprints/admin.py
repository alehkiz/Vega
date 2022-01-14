from app.models.app import FilePDF, FilePDFType
from app.models.notifier import Notifier
from flask import (
    current_app as app,
    Blueprint,
    render_template,
    url_for,
    redirect,
    flash,
    json,
    request,
    g,
)
from flask_security import current_user, login_required
from flask_security import roles_accepted
from datetime import datetime

from sqlalchemy.orm import relationship

from sqlalchemy import inspect, desc, asc, func

from app.models.wiki import Article, Topic, User, Question, Tag, SubTopic
from app.forms.wiki import ArticleForm
from app.forms.question import QuestionFilter
from app.core.db import db
from app.utils.routes import counter

bp = Blueprint("admin", __name__, url_prefix="/admin/")


@bp.before_request
@login_required
@roles_accepted("admin", 'support', 'manager_user', 'manager_content')
def before_request():
    pass


@bp.route("/")
@login_required
@roles_accepted("admin", 'support', 'manager_user', 'manager_content')
def index():
    return render_template("base.html")


@bp.route("/users/")
@login_required
@roles_accepted("admin", 'manager_user')
def users():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    if not order is False:
        try:
            column = getattr(User, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = User.id
            column_type = User.id.desc
    else:
        column = User.id
        column_type = column.desc
    u = User.query.filter(User.active == True).order_by(column_type())
    paginate = u.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    # paginate = User.query.paginate(page, app.config.get('TABLE_ITEMS_PER_PAGE', 10), False)
    first_page = list(paginate.iter_pages())[0]
    order_type = "asc" if order_type == "desc" else "desc"
    last_page = paginate.pages  # list(paginate.iter_pages())[-1]
    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint="admin.users",
        cls_table=User,
        list=True,
        page_name="Usuários",
        order_type=order_type,
    )


@bp.route("/articles/")
@login_required
@roles_accepted("admin")
def articles():
    page = request.args.get("page", 1, type=int)
    paginate = Article.query.paginate(
        page, app.config.get("TABLE_ITEMS_PER_PAGE", 10), False
    )
    first_page = list(paginate.iter_pages())[0]
    last_page = (
        paginate.pages
    )  # list(paginate.iter_pages())[-1] if list(paginate.iter_pages())[-1] != first_page else None
    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=Article,
        list=True,
        page_name="Artigos",
    )


@bp.route("/respostas")
@login_required
@roles_accepted("admin", 'support', 'manager_user', 'manager_content')
def answers():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    order_dict = {'desc': desc, 'asc': asc}
    topic = request.args.get('topic', False)
    form = QuestionFilter(request.args, meta={'csrf': False})
    search = request.args.get('search', False)
    request_args = request.args
    if topic != False:
        topic = Topic.query.filter(Topic.name.ilike(topic)).first()
    if not order_type in order_dict.keys():
        order_type = 'desc'
    if not order is False or not order_type is False:
        try:
            column = getattr(Question, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = Question.id
            column_type = Question.id.desc
    else:
        column = Question.id
        column_type = column.desc

    # TODO Incluir a odernação por relacionamento de acordo com a seleção do usuário
    relations = inspect(Question).relationships
    if hasattr(column.property, 'target'):
        if column.property.key in relations:
            relationship = getattr(relations, str(
                column.property.key), False)
            if relationship is False:
                raise Exception(
                    f'{column.property.key} não é um relacionamento em Question')
            q = db.session.query(Question).filter(Question.answer != None, Question.answer_approved == True).join(relationship.mapper.class_, getattr(
                Question, str(column.property.key))).order_by(order_dict[order_type](getattr(relationship.mapper.class_, 'name')))
    else:
        q = Question.query.filter(
            Question.answer != None, Question.answer_approved == True).order_by(column_type())

    if form.validate():
        if len(form.topic.data) > 0:
            q = q.join(Question.topics).filter(Topic.id.in_(
                [_.id for _ in form.topic.data]))
        if len(form.sub_topic.data) > 0:
            q = q.filter(Question.sub_topic_id.in_(
                [_.id for _ in form.sub_topic.data]))
        if len(form.tag.data) > 0:
            q = q.filter(Question.tags.any(
                Tag.id.in_([_.id for _ in form.tag.data])))
    if search != False and search != '' and search != None:
        q = q.filter((
            func.ts_rank_cd(
                Question.search_vector, func.plainto_tsquery(
                    'public.pt', search))) > 0)

    paginate = q.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )

    last_page = paginate.pages
    order_type = "asc" if order_type == "desc" else "desc"

    url_args = dict(request.args)
    url_args.pop('page') if 'page' in url_args.keys() else None

    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=Question,
        list=True,
        page_name="Respostas",
        order_type=order_type,
        request_args=request_args,
        _topic=Topic.query.filter(Topic.selectable == True),
        _sub_topic=SubTopic.query,
        form=form,
        url_args=url_args
    )


@bp.route("/perguntas")
# @login_required
@roles_accepted("admin", 'support', 'manager_user', 'manager_content')
def questions():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    topic = request.args.get("topic", False)
    form = QuestionFilter(request.args, meta={'csrf': False})
    search = request.args.get('search', False)
    request_args = request.args
    if topic != False and not topic.isnumeric():
        topic = Topic.query.filter(Topic.name.ilike(topic)).first()
    elif topic != False and topic.isnumeric():
        topic = Topic.query.filter(Topic.id == int(topic)).first()
    

    if not order is False or not order_type is False:
        try:
            column = getattr(Question, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = Question.create_at
            column_type = Question.create_at.asc
    else:
        column = Question.create_at
        column_type = column.asc
    if order:
        if order in Question.__table__.columns:
            if topic != False:
                q = db.session.query(Question).filter(
                    Question.answer == None).join(Question.topics).filter(Topic.id == topic.id).order_by(column_type())
                # q = Question.query.filter(
                #     Question.answer == None, Question.topic_id == topic.id
                # ).order_by(column_type())
            else:
                q = db.session.query(Question).filter(
                    Question.answer == None).order_by(column_type())
                # Question.query.filter(Question.answer == None).order_by(
                #     column_type()
                # )
        else:
            relationship_class = getattr(
                Question, order).property.mapper.class_
            relationship_type = getattr(Question, order)
            relationship_type_order = getattr(
                relationship_class.name, order_type)
            if topic != False:
                q = (
                    db.session.query(Question)
                    .filter(Question.answer == None)
                    .join(Question.topics)
                    .filter(Topic.id == topic.id)
                    .join(relationship_class, relationship_type)
                    .order_by(relationship_type_order())
                )
            else:
                q = (
                    db.session.query(Question)
                    .filter(Question.answer == None)
                    .join(relationship_class, relationship_type)
                    .order_by(relationship_type_order())
                )
    else:
        # if topic != False:
        #     q = Question.query.filter(
        #         Question.answer == None, Question.topic_id == topic.id
        #     ).order_by(Question.create_at.asc())
        # else:
        #     q = Question.query.filter(Question.answer == None).order_by(
        #         Question.create_at.asc()
        #     )
        if topic != False:
            q = db.session.query(Question).filter(
                Question.answer == None).join(Question.topics).filter(Topic.id == topic.id).order_by(column_type())
            # q = Question.query.filter(
            #     Question.answer == None, Question.topic_id == topic.id
            # ).order_by(column_type())
        else:
            q = db.session.query(Question).filter(
                Question.answer == None).order_by(column_type())
            # Question.query.filter(Question.answer == None).order_by(
            #     column_type()
            # )
    
    if form.validate():
        if len(form.topic.data) > 0:
            q = q.join(Question.topics).filter(Topic.id.in_(
                [_.id for _ in form.topic.data]))
        if len(form.sub_topic.data) > 0:
            q = q.filter(Question.sub_topic_id.in_(
                [_.id for _ in form.sub_topic.data]))
        if len(form.tag.data) > 0:
            q = q.filter(Question.tags.any(
                Tag.id.in_([_.id for _ in form.tag.data])))
    
    if search != False and search != '' and search != None:
        q = q.filter((
            func.ts_rank_cd(
                Question.search_vector, func.plainto_tsquery(
                    'public.pt', search))) > 0)
    paginate = q.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    order_type = "asc" if order_type == "desc" else "desc"

    url_args = dict(request.args)
    url_args.pop('page') if 'page' in url_args.keys() else None

    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=Question,
        list=True,
        page_name="Dúvidas pendentes de respostas",
        order_type=order_type,
        mode="question",
        type='responder',
        _topic=Topic.query.filter(Topic.selectable == True),
        _sub_topic=SubTopic.query,
        request_args=request_args,
        form=form,
        url_args=url_args
    )


@bp.route("/aprovar")
@login_required
@roles_accepted("admin", "support", "manager_content")
def to_approve():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    topic = request.args.get("topic", False)
    form = QuestionFilter(request.args, meta={'csrf': False})
    search = request.args.get('search', False)
    request_args = request.args
    if topic != False and not topic.isnumeric():
        topic = Topic.query.filter(Topic.name.ilike(topic)).first()
    elif topic != False and topic.isnumeric():
        topic = Topic.query.filter(Topic.id == int(topic)).first()

    if not order is False or not order_type is False:
        try:
            column = getattr(Question, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = Question.id
            column_type = Question.id.desc
    else:
        column = Question.id
        column_type = column.desc
    if order:
        if order in Question.__table__.columns:
            if topic:
                q = Question.query.filter(
                    Question.answer != None,
                    Question.answer_approved == False,
                ).join(Question.topics
                ).filter(Topic.id == topic.id
                ).order_by(column_type())
            else:
                q = Question.query.filter(
                    Question.answer != None, Question.answer_approved == False
                ).order_by(column_type())
        else:
            relationship_class = getattr(
                Question, order).property.mapper.class_
            relationship_type = getattr(Question, order)
            relationship_type_order = getattr(
                relationship_class.name, order_type)
            if topic != False:
                q = (
                    db.session.query(Question)
                    .filter(
                        Question.answer != None,
                        Question.answer_approved == False,
                    ).join(Question.topics
                    ).filter(Topic.id == topic.id)
                    .join(relationship_class, relationship_type)
                    .order_by(relationship_type_order())
                )
            else:
                q = (
                    db.session.query(Question)
                    .filter(Question.answer != None, Question.answer_approved == False)
                    .join(relationship_class, relationship_type)
                    .order_by(relationship_type_order())
                )
    else:
        if topic != False:
            q = db.session.query(Question).filter(Question.answer != None, Question.answer_approved == False).join(
                Question.topics).filter(Topic.id == topic.id).order_by(Question.create_at.asc())
            # Question.query.filter(
            #     Question.answer != None,
            #     Question.answer_approved == False,
            #     Question.topic_id == topic.id,
            # ).order_by(Question.create_at.asc())
        else:
            q = Question.query.filter(
                Question.answer != None, Question.answer_approved == False
                # ).order_by(asc(Question.create_at))
            ).order_by(Question.create_at.asc())

    if form.validate():
        if len(form.topic.data) > 0:
            q = q.filter(Topic.id.in_(
                [_.id for _ in form.topic.data]))
        if len(form.sub_topic.data) > 0:
            q = q.filter(Question.sub_topic_id.in_(
                [_.id for _ in form.sub_topic.data]))
        if len(form.tag.data) > 0:
            q = q.filter(Question.tags.any(
                Tag.id.in_([_.id for _ in form.tag.data])))
    if search != False and search != '' and search != None:
        q = q.filter((
            func.ts_rank_cd(
                Question.search_vector, func.plainto_tsquery(
                    'public.pt', search))) > 0)
    paginate = q.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    order_type_inverse = "asc" if order_type == "desc" else "desc"
    order = request.args.get('order', False)
    url_args = dict(request.args)
    print(order)
    url_args.pop('order_type', None)
    url_args.pop('order', None)
    print(order)
    url_args.pop('page') if 'page' in url_args.keys() else None
    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=Question,
        list=True,
        page_name="Dúvidas",
        order_type=order_type,
        order=order,
        mode="question",
        type="aprovar",
        form=form,
        url_args=url_args,
        order_type_inverse = order_type_inverse
    )


@bp.route("/topic")
@login_required
@roles_accepted("admin")
def topic():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    if not order is False or not order_type is False:
        try:
            column = getattr(Topic, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = Topic.id
            column_type = Topic.id.desc
    else:
        column = Topic.id
        column_type = column.desc
    t = Topic.query.order_by(column_type())
    paginate = t.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    order_type = "asc" if order_type == "desc" else "desc"
    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=Topic,
        list=True,
        page_name="Topics",
        order_type=order_type,
    )


@bp.route("/sub_topic")
@login_required
@roles_accepted("admin")
def sub_topic():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    if not order is False or not order_type is False:
        try:
            column = getattr(SubTopic, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = SubTopic.id
            column_type = SubTopic.id.desc
    else:
        column = SubTopic.id
        column_type = column.desc
    t = SubTopic.query.order_by(column_type())
    paginate = t.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    order_type = "asc" if order_type == "desc" else "desc"
    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=SubTopic,
        list=True,
        page_name="SubTopics",
        order_type=order_type,
    )

@bp.route("/file_pdf_type")
@login_required
@roles_accepted("admin")
def file_pdf_type():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    if not order is False or not order_type is False:
        try:
            column = getattr(FilePDFType, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = FilePDFType.id
            column_type = FilePDFType.id.desc
    else:
        column = FilePDFType.id
        column_type = column.desc
    t = FilePDFType.query.order_by(column_type())
    paginate = t.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    order_type = "asc" if order_type == "desc" else "desc"
    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=FilePDFType,
        list=True,
        page_name="FilePDFType",
        order_type=order_type,
        no_view=False
    )

@bp.route("/tag")
@login_required
@roles_accepted("admin")
def tag():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    order_dict = {'desc': desc, 'asc': asc}
    if not order_type in order_dict.keys():
        order_type = 'desc'
    if not order is False or not order_type is False:
        try:
            column = getattr(Tag, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = Tag.id
            column_type = Tag.id.desc
    else:
        column = Tag.id
        column_type = column.desc
    # TODO Incluir a odernação por relacionamento de acordo com a seleção do usuário
    relations = inspect(Tag).relationships
    if hasattr(column.property, 'target'):
        if column.property.target.name in relations:
            relationship = getattr(relations, str(
                column.property.target.name), False)
            if relationship is False:
                raise Exception(
                    f'{column.property.target.name} não é um relacionamento em Tag')
            q = db.session.query(Tag).join(relationship.mapper.class_, getattr(Tag, str(
                column.property.target.name))).order_by(order_dict[order_type](getattr(relationship.mapper.class_, 'name')))
    else:
        q = Tag.query.order_by(column_type())
    paginate = q.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    order_type = "asc" if order_type == "desc" else "desc"
    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=Tag,
        list=True,
        page_name="Notificações",
        order_type=order_type,
    )


@bp.route('/notifier')
@login_required
@roles_accepted('admin')
def notifier():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    order_dict = {'desc': desc, 'asc': asc}
    if not order_type in order_dict.keys():
        order_type = 'desc'
    if not order is False or not order_type is False:
        try:
            column = getattr(Notifier, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = Notifier.id
            column_type = Notifier.id.desc
    else:
        column = Notifier.id
        column_type = column.desc
    # TODO Incluir a odernação por relacionamento de acordo com a seleção do usuário
    relations = inspect(Notifier).relationships
    if hasattr(column.property, 'target'):
        if column.property.target.name in relations:
            relationship = getattr(relations, str(
                column.property.target.name), False)
            if relationship is False:
                raise Exception(
                    f'{column.property.target.name} não é um relacionamento em Notifier')
            q = db.session.query(Notifier).join(relationship.mapper.class_, getattr(Notifier, str(
                column.property.target.name))).order_by(order_dict[order_type](getattr(relationship.mapper.class_, 'name')))
    else:
        q = Notifier.query.order_by(column_type())
    paginate = q.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    order_type = "asc" if order_type == "desc" else "desc"

    url_args = dict(request.args)
    url_args.pop('page') if 'page' in url_args.keys() else None

    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=Notifier,
        list=True,
        page_name="Notificações",
        order_type=order_type,
        url_args=url_args
    )



@bp.route('/file')
@login_required
@roles_accepted('admin', 'suporte')
def file():
    page = request.args.get("page", 1, type=int)
    order = request.args.get("order", False)
    order_type = request.args.get("order_type", "desc")
    topic = request.args.get("topic", None)
    # form = QuestionFilter(request.args, meta={'csrf': False})
    request_args = request.args
    if topic != False and not topic.isnumeric():
        topic = Topic.query.filter(Topic.name.ilike(topic)).first()
    elif topic != False and topic.isnumeric():
        topic = Topic.query.filter(Topic.id == int(topic)).first()
    if not order is False or not order_type is False:
        try:
            column = getattr(FilePDF, order)
            column_type = getattr(column, order_type)
        except Exception as e:
            column = FilePDF.uploaded_at
            column_type = FilePDF.uploaded_at.asc
    else:
        column = FilePDF.uploaded_at
        column_type = column.asc
    if order:
        if order in FilePDF.__table__.columns:
            if topic != False:
                q = db.session.query(FilePDF).join(FilePDF.topics).filter(Topic.id == topic.id).order_by(column_type())
                # q = Question.query.filter(
                #     Question.answer == None, Question.topic_id == topic.id
                # ).order_by(column_type())
            else:
                q = db.session.query(FilePDF).order_by(column_type())
                # Question.query.filter(Question.answer == None).order_by(
                #     column_type()
                # )
        else:
            relationship_class = getattr(
                FilePDF, order).property.mapper.class_
            relationship_type = getattr(FilePDF, order)
            relationship_type_order = getattr(
                relationship_class.name, order_type)
            if topic != False:
                q = (
                    db.session.query(FilePDF)
                    .join(Question.topics)
                    .filter(Topic.id == topic.id)
                    .join(relationship_class, relationship_type)
                    .order_by(relationship_type_order())
                )
            else:
                q = (
                    db.session.query(FilePDF)
                    .join(relationship_class, relationship_type)
                    .order_by(relationship_type_order())
                )
    else:
        # if topic != False:
        #     q = Question.query.filter(
        #         Question.answer == None, Question.topic_id == topic.id
        #     ).order_by(Question.create_at.asc())
        # else:
        #     q = Question.query.filter(Question.answer == None).order_by(
        #         Question.create_at.asc()
        #     )
        if topic != False:
            q = db.session.query(FilePDF).join(FilePDF.topics).filter(Topic.id == topic.id).order_by(column_type())
            # q = Question.query.filter(
            #     Question.answer == None, Question.topic_id == topic.id
            # ).order_by(column_type())
        else:
            q = db.session.query(FilePDF).order_by(column_type())
            # Question.query.filter(Question.answer == None).order_by(
            #     column_type()
            # )
    # if form.validate():
    #     if len(form.topic.data) > 0:
    #         q = q.join(Question.topics).filter(Topic.id.in_(
    #             [_.id for _ in form.topic.data]))
    #     if len(form.sub_topic.data) > 0:
    #         q = q.filter(Question.sub_topic_id.in_(
    #             [_.id for _ in form.sub_topic.data]))
    #     if len(form.tag.data) > 0:
    #         q = q.filter(Question.tags.any(
    #             Tag.id.in_([_.id for _ in form.tag.data])))
    paginate = q.paginate(page, app.config.get(
        "TABLE_ITEMS_PER_PAGE", 10), False)
    first_page = (
        list(paginate.iter_pages())[0]
        if len(list(paginate.iter_pages())) >= 1
        else None
    )
    last_page = paginate.pages
    order_type = "asc" if order_type == "desc" else "desc"

    url_args = dict(request.args)
    url_args.pop('page') if 'page' in url_args.keys() else None

    return render_template(
        "admin.html",
        pagination=paginate,
        first_page=first_page,
        last_page=last_page,
        endpoint=request.url_rule.endpoint,
        cls_table=FilePDF,
        list=True,
        page_name="Arquivos",
        order_type=order_type,
        type='aprovar',
        _topic=Topic.query.filter(Topic.selectable == True),
        _sub_topic=SubTopic.query,
        request_args=request_args,
        url_args=url_args
    )