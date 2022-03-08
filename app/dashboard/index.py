from unicodedata import category
from dash_bootstrap_components._components.Alert import Alert
from dash_html_components.B import B
from dash_html_components.Br import Br
import dash_table
from sqlalchemy.sql.expression import column, label
from sqlalchemy import extract
from sqlalchemy.sql.functions import now
from app.models.app import Visit
from app.models.search import Search, SearchDateTime
from app.utils.kernel import format_number_as_thousand
import datetime
from re import template
from dash_core_components.Checklist import Checklist
# from flask import config, url_for, app as current_app
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash_table import DataTable

from flask import current_app as app

import dash_bootstrap_components as dbc
from flask.templating import render_template
import plotly.express as px
import pandas as pd
from app.models.wiki import Question, SubTopic, Topic, Tag, QuestionView
from app.models.security import User
from app.core.db import db
from sqlalchemy import func, asc, inspect, text, or_
from sqlalchemy.sql.expression import literal_column


def get_graph_tags():
    df = pd.read_sql(db.session.query(Tag.name.label('Marcação'), func.count(Question.id).label(
        'Total')).outerjoin(Question.tags).group_by(Tag).statement, con=db.session.bind)
    df['Marcação'].replace({None: 'Vazio'}, inplace=True)
    graph = px.pie(df, values='Total', names='Marcação', title='Marcações')
    return graph


def get_graph_topics():
    df = pd.read_sql(db.session.query(Topic.name.label('Nome'), Topic.selectable.label('Selecionável'), func.count(Question.id).label(
        'Total')).filter(Topic.selectable == True, Topic.active == True).outerjoin(Question.topics).group_by(Topic).statement, con=db.session.bind)
    graph = px.pie(df, values='Total', names='Nome', title='Tópicos')
    return graph


def get_graph_sub_topics():
    df = pd.read_sql(db.session.query(SubTopic.name.label('Nome'), func.count(Question.id).label('Total')).filter(or_(
        QuestionView.user_id == 4, QuestionView.user_id == None)).outerjoin(Question).group_by(SubTopic).statement, con=db.session.bind)
    graph = px.pie(df, values='Total', names='Nome', title='Sub-Tópicos')
    return graph


def get_graph_questions_by_month(names=None):
    df = pd.read_sql(db.session.query(func.count(Question.id).label('Total'),
                                      func.date_trunc('month', Question.create_at).label(
                                          'Mês'), Topic.name.label('Assunto')
                                      ).filter(or_(QuestionView.user_id == 4, QuestionView.user_id == None)).join(Topic.questions).group_by('Mês', 'Assunto').order_by(asc('Mês')
                                                                                                                                                                       ).statement, db.session.bind)
    if df.empty is True:
        df.Total = pd.Series([0])
        df.at[0, 'Mês'] = None
        df.at[0, 'Assunto'] = ' '
    if names == None:
        return px.line(df, x='Mês', y='Total', title='Dúvidas cadastradas por dia e assunto', color='Assunto', hover_data={'Mês': "|%m/%Y"})
    mask = df.Assunto.isin(names)
    graph = px.line(df[mask], x='Mês', y='Total', title='Dúvidas cadastradas por dia e assunto',
                    color='Assunto', hover_data={'Mês': "|%m/%Y"})
    return graph


def get_questions_views_by_date():
    df = pd.read_sql(
        db.session.query(
            func.count(QuestionView.id).label('Total'), func.date_trunc('day', QuestionView.datetime).label('Data')).filter(
                or_(QuestionView.user_id == 4, QuestionView.user_id == None)).filter(
                    extract('isodow', QuestionView.datetime) < 7
                ).group_by(
            'Data'
        ).order_by(
            asc('Data')).statement, con=db.session.bind)
    df.Data = df.Data.dt.date
    graph = px.line(df, x='Data', y='Total',
                    title='Perguntas visualizadas por dia')
    return graph


def get_graph_questions_answers_by_date():
    df = pd.read_sql(
        db.session.query(func.count(Question.id).label('Total'),
                         func.date_trunc('day', Question.answer_at).label('Data')).group_by('Data').order_by(asc('Data')).statement, con=db.session.bind)
    a1 = db.session.query(func.count(Question.id).label('Total'), func.date_trunc('day', Question.create_at).label(
        "Data"), literal_column("'Perguntas'").label('Tipo')).group_by('Data').order_by("Data")
    a2 = db.session.query(func.count(Question.id).label('Total'), func.date_trunc('day', Question.answer_at).label(
        'Data'), literal_column("'Respostas'").label('Tipo')).group_by('Data').order_by("Data")

    result = a1.union(a2)
    df = pd.read_sql(result.statement, con=db.session.bind)
    # df = pd.read_sql(
    #     db.session.query(func.count(Question.id).label('Total'),
    #         func.date_trunc('day', Question.answer_at).label('Data')).group_by('Data').order_by(asc('Data')).statement, con=db.session.bind)
    # db.session.query(func.count(Question.id).label('Respostas'), func.date_trunc('day', Question.answer_at).label('Data')).filter(Question.answer != None).group_by('Data').order_by(asc('Data'))
    df.Data = df.Data.dt.date
    df = df.sort_values('Data')
    graph = px.line(df, x='Data', y='Total', color='Tipo',
                    title='Perguntas e respostas por dia')
    return graph


def get_graph_search_by_date():
    df = pd.read_sql(
        db.session.query(func.count(SearchDateTime.id).label('Pesquisas'),
                         func.date_trunc(
                             'day', SearchDateTime.search_datetime).label('Data')
                         ).filter(
                             extract(
                                 'isodow', SearchDateTime.search_datetime) < 7
        ).group_by(
                             'Data').order_by(
                                 asc('Data')
        ).statement, con=db.session.bind)

    df.Data = df.Data.dt.date
    graph = px.line(df, x='Data', y='Pesquisas', title='Pesquisas por dia')
    return graph


def get_graph_access_by_date():
    df = pd.read_sql(
        db.session.query(
            func.count(Visit.id).label('Total'),
            func.date_trunc('day', Visit.datetime).label('Data'),
            Topic.name.label('Topico')
            ).outerjoin(
                Topic
            ).filter(
            or_(Visit.user_id == 4, Visit.user_id == None)).filter(
            extract('isodow', Visit.datetime) < 7
        ).group_by('Data', 'Topico').order_by(
            asc('Data')).statement, con=db.session.bind)
    df.Data = df.Data.dt.date
    df.Topico.replace([None], 'Nenhum', inplace=True)
    # print(df.columns)
    graph = px.line(df, x='Data', y='Total', color='Topico', title='Acessos por dia')
    return graph


def get_user_answers():
    df = pd.read_sql(
        db.session.query(
            User.name.label('Nome'),
            func.count(
                Question.id).label('Total')).outerjoin(
                    Question.answered_by).group_by(User).filter(Question.answer_approved==True).order_by(
                        func.count(Question.id).desc()).statement, con=db.session.bind
    )
    df['%'] = df.Total.apply(lambda x: float((x / df.Total.sum()) * 100))
    df['%'] = df['%'].round(decimals=2)

    return dash_table.DataTable(
        id='table',
        columns=[{'name': i, 'id': i} for i in df.columns],
        data=df.to_dict('records'),
        editable=False,
        sort_action='native',
        style_as_list_view=True,
        style_cell={'padding': '5px'},
        style_header={
            'backgroundColor': 'gray',
            'fontWeight': 'bold'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
    )


def get_user_approve():
    df = pd.read_sql(
        db.session.query(
            User.name.label('Nome'),
            func.count(Question.id).label('Total')).outerjoin(Question.approved_by).group_by(User).filter(Question.answer_approved == True).order_by(func.count(Question.id).desc()).statement, con=db.session.bind
    )
    df['%'] = df.Total.apply(lambda x: float((x / df.Total.sum()) * 100))
    df['%'] = df['%'].round(decimals=2)

    return dash_table.DataTable(
        id='table',
        columns=[{'name': i, 'id': i} for i in df.columns],
        data=df.to_dict('records'),
        editable=False,
        sort_action='native',
        style_as_list_view=True,
        style_cell={'padding': '5px'},
        style_header={
            'backgroundColor': 'gray',
            'fontWeight': 'bold'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        },
    )


def get_total_access():
    return Visit.query.filter(
        or_(Visit.user_id == 4, Visit.user_id == None),
        extract('isodow', Visit.datetime) < 7).count()


def access_last_month():
    lastmonth = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    query = db.session.query(func.count(Visit.id).label('Total')).filter(
        extract('month', Visit.datetime) == lastmonth.month,
        extract('year', Visit.datetime) == lastmonth.year,
        extract('isodow', Visit.datetime) < 7)
    return query.all()[0].Total

    return QuestionView.query_by_month_year(lastmonth.year, lastmonth.month).count()


def get_question_view_current_month():
    return QuestionView.query_by_month_year(datetime.date.today().year, datetime.date.today().month).count()


def get_total_search():
    return SearchDateTime.query.filter(or_(SearchDateTime.search_user_id == 4, SearchDateTime.search_user_id == None)).count()

def get_search_today():
    return SearchDateTime.query.filter(or_(SearchDateTime.search_user_id == 4, SearchDateTime.search_user_id == None)).filter(func.date_trunc('day', SearchDateTime.search_datetime) == datetime.date.today()).count()

def get_question_views_today():
    return QuestionView.query.filter(or_(QuestionView.user_id == 4, QuestionView.user_id == None)).filter(func.date_trunc('day', QuestionView.datetime) == datetime.date.today()).count()

def get_total_questions_views():
    return QuestionView.query.filter(or_(QuestionView.user_id == 4, QuestionView.user_id == None)).count()


def get_questions_answered():
    return Question.query.filter(Question.active == True, Question._answer != '', Question.answer_approved == True).count()


def get_report_last_month():
    last_month = datetime.date.today().replace(days=1) - datetime.timedelta(days=1)
    return Question.query.filter(
        Question.active == True,
        Question._answer != '',
        Question.answer_approved == True
    ).filter(
        extract(
            'year',
            Question.answer_approved_at) == last_month.year
    ).filter(
        extract(
            'month',
            Question.answer_approved_at) == last_month.month
    )


def get_mean_question_view_by_bussiness_day():
    query = db.session.query(
        func.count(QuestionView.id).label('Total'),
        func.date_trunc('day', QuestionView.datetime).label('Date')).filter(
            extract('isodow', QuestionView.datetime) < 7).group_by(
                'Date'
            )
    days_count = query.count()
    days_sum = sum([_[0] for _ in query])
    return int(round(days_sum / days_count, 0))

def get_mean_visit_by_bussiness_day():
    query = db.session.query(
        func.count(Visit.id).label('Total'),
        func.date_trunc('day', Visit.datetime).label('Date')).filter(
            extract('isodow', Visit.datetime) < 7).group_by(
                'Date'
            )
    days_count = query.count()
    days_sum = sum([_[0] for _ in query])
    return int(round(days_sum / days_count, 0))

def get_total_visit_by_bussiness_day_in_current_month():
    query = db.session.query(func.count(Visit.id).label('Total')).filter(
        extract('month', Visit.datetime) == datetime.date.today().month,
        extract('year', Visit.datetime) == datetime.date.today().year,
        extract('isodow', Visit.datetime) < 7
    )
    return query.all()[0].Total

def get_mean_visit_by_bussiness_day_month():
    query = db.session.query(
        func.count(Visit.id).label('Total'),
        func.date_trunc('month', Visit.datetime).label('Month')).filter(
            extract('isodow', Visit.datetime) < 7).group_by(
                'Month'
            )
    months_count = query.count()
    months_sum = sum([_[0] for _ in query])
    return int(round(months_sum / months_count, 0))

def get_visits_today():
    query = db.session.query(
        func.count(Visit.id).label('Total'),
        # func.date_trunc('day', Visit.datetime).label('Date')
        ).filter(
            or_(Visit.user_id == 4, Visit.user_id == None),
            func.date_trunc('day', Visit.datetime) == datetime.date.today(),
            extract('isodow', Visit.datetime) < 7
        )#.group_by(
            # 'Date'
        # )
    return query.all()[0].Total

def dash_app(app=False):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashapp/',
                    external_stylesheets=[dbc.themes.BOOTSTRAP], update_title='Atualizando...')

    engine = db.get_engine(app)
    if not inspect(engine).dialect.has_table(engine.connect(), table_name='topic'):
        dash_app.layout = html.Div()
    else:
        topics = [x.name for x in Topic.query]
        dash_app.layout = dbc.Container([
            dcc.Store(id='store'),
            dbc.Jumbotron(
                [
                    html.H1(
                        f"Dashboard {app.config['SITE_TITLE']}", className="display-5"),
                    html.Div(id='updater_values')

                    # html.P(dbc.Button("Learn more", color="primary"), className="lead"),
                ], className='p-3', id='jumbo'
            ),
            # dbc.Tabs([
            #     dbc.Tab(label='Acessos por dia', tab_id='access_day'),
            #     dbc.Tab(label='Questões visualizadas por dia', tab_id='views_day'),
            #     dbc.Tab(label='Perguntas por tópicos e tags', tab_id='tags_topics')
            # ], id='tabs',
            # active_tab='access_day'),
            # html.Div(id='tab_content', className='p-4'),
            dbc.Tabs([
                dbc.Tab(label='Evolução diária', tab_id='diary', children=[
                    dbc.Tabs([
                        dbc.Tab(label='Acessos', tab_id='diary-access'),
                        dbc.Tab(label='Visualizações de perguntas',
                                tab_id='diary-questions-views'),
                        dbc.Tab(label='Perguntas e Respostas',
                                tab_id='diary-questions-answers'),
                        dbc.Tab(label='Pesquisas por dia',
                                tab_id='diary-searches')
                        # dbc.Tab(label='', tab_id='diary-'),
                    ], id='diary-tab', active_tab='diary-access')]),
                dbc.Tab(label='Comparativos percentuais', tab_id='percent', children=[
                    dbc.Tabs([
                        dbc.Tab(label='Marcações', tab_id='percent-tags'),
                        dbc.Tab(label='Tópicos', tab_id='percent-topics'),
                        dbc.Tab(label='Sub-Tópicos',
                                tab_id='percent-sub-topics'),
                    ], id='percent-tab', active_tab='percent-tags')]),
                dbc.Tab(label='Top respostas', tab_id='user', children=[
                    dbc.Tabs([
                        dbc.Tab(label='Respostas', tab_id='user-answers'),
                        dbc.Tab(label='Aprovações', tab_id='user-approve')
                    ], id='user-tab', active_tab='user-answers')]),
            ], id='tabs', active_tab='diary'),
            html.Div(id='tab_content', className='p-4'),
            dcc.Interval(id='interval-component',
                         interval=30000,  # 30 segundos
                         n_intervals=0)  # contador para atualização
        ])

    @dash_app.callback(
        Output('tab_content', 'children'),
        Input('tabs', 'active_tab'),
        Input('diary-tab', 'active_tab'),
        Input('percent-tab', 'active_tab'),
        Input('user-tab', 'active_tab'))
    def render_tabs(tab, *params):
        tab_name = tab.split('-')[0]
        active_subtab = [_ for _ in params if tab_name in _]
        if len(active_subtab) == 1:
            active_subtab = active_subtab[0]
            if active_subtab == 'diary-access':
                return dcc.Graph(figure=get_graph_access_by_date(), config={'displayModeBar': False})
            elif active_subtab == 'diary-questions-views':
                return dcc.Graph(figure=get_questions_views_by_date(), config={'displayModeBar': False})
            elif active_subtab == 'diary-questions-answers':
                return dcc.Graph(figure=get_graph_questions_answers_by_date(), config={'displayModeBar': False})
            elif active_subtab == 'percent-tags':
                return dcc.Graph(figure=get_graph_tags(), config={'displayModeBar': False})
            elif active_subtab == 'percent-topics':
                return dcc.Graph(figure=get_graph_topics(), config={'displayModeBar': False})
            elif active_subtab == 'percent-sub-topics':
                return dcc.Graph(figure=get_graph_sub_topics(), config={'displayModeBar': False})
            elif active_subtab == 'user-answers':
                return get_user_answers()
            elif active_subtab == 'user-approve':
                return get_user_approve()
            elif active_subtab == 'diary-searches':
                print('aqui')
                return dcc.Graph(figure=get_graph_search_by_date(), config={'displayModeBar': False})
        else:
            return 'Nenhuma seleção'

    @dash_app.callback(
        Output('updater_values', 'children'),
        Input('interval-component', 'n_intervals'))
    def updater(n):
        # print(n)

        perc_comp_last_month = round((get_total_visit_by_bussiness_day_in_current_month() / get_mean_visit_by_bussiness_day_month()) *100 , 2)
        perc_comp_today = round((get_visits_today() / get_mean_visit_by_bussiness_day()) * 100, 2)
        perc_comp_question_today = round((get_question_views_today() / get_mean_question_view_by_bussiness_day()) * 100, 2)
        if perc_comp_last_month >= 100:
            current_month_color_symbol='fas fa-arrow-up'
            color_current_month = 'text-success'
        else:
            current_month_color_symbol='fas fa-arrow-down'
            color_current_month = 'text-danger'
        if perc_comp_today >= 100:
            current_day_color_symbol='fas fa-arrow-up'
            color_current_day = 'text-success'
        else:
            current_day_color_symbol='fas fa-arrow-down'
            color_current_day = 'text-danger'
        if perc_comp_question_today >= 100:
            question_view_color_symbol='fas fa-arrow-up'
            color_question_view = 'text-success'
        else:
            question_view_color_symbol='fas fa-arrow-down'
            color_question_view = 'text-danger'


        return [
            dbc.Row(
            # html.Div([
                html.Div([
                html.Div([
                html.Div('Acessos Totais', className='card-header'),
                html.Div([
                    html.B(format_number_as_thousand(get_total_access()))
                    ], className='card-body')], className='card mx-1 mb-2'),
                html.Div([
                html.Div('Acessos Mês Anterior', className='card-header'),
                html.Div([
                    html.B(format_number_as_thousand(access_last_month()))
                    ], className='card-body')], className='card mx-1 mb-2'),
                html.Div([
                    html.Div('Acessos Mês Atual', className='card-header'),
                    html.Div([
                    html.B(format_number_as_thousand(get_total_visit_by_bussiness_day_in_current_month())),
                    html.Hr(), 
                    html.P([
                        html.I(className=current_month_color_symbol + ' ' + color_current_month),
                        html.B(perc_comp_last_month, className=color_current_month),
                        html.P('% comparado com a média mensal', className='card-text d-inline fw-light')], className='d-inline')
                    ], className='card-body')], className='card mx-1 mb-2'),
                
                html.Div([
                    html.Div('Acessos Hoje', className='card-header'),
                    html.Div([
                    html.B(format_number_as_thousand(get_visits_today())),
                    html.Hr(), 
                    html.P([
                        html.I(className=current_day_color_symbol + ' ' + color_current_day),
                        html.B(perc_comp_today, className=color_current_day),
                        html.P('% comparado com a média diária', className='card-text d-inline fw-light')], className='d-inline')
                    ], className='card-body')], className='card mx-1 mb-2'),
                ], className='card-group')
                # ], className='col-sm-4'), className='p-2'
        ),
        html.Hr(),
        dbc.Row(
            html.Div(
                html.Div([
                    html.Div([
                    html.Div('Perguntas Respondidas', className='card-header'),
                    html.Div([
                        html.B(format_number_as_thousand(get_questions_answered()))
                        ], className='card-body')], className='card mx-1 mb-2'),
                html.Div([
                    html.Div('Perguntas visualizadas', className='card-header'),
                    html.Div([
                    html.B(format_number_as_thousand(get_total_questions_views()))
                    ], className='card-body')], className='card mx-1 mb-2'),
                html.Div([
                    html.Div('Perguntas visualizadas hoje', className='card-header'),
                    html.Div([
                    html.B(format_number_as_thousand(get_question_views_today())),
                    html.Hr(), 
                    html.P([
                        html.I(className=question_view_color_symbol + ' ' + color_question_view),
                        html.B([perc_comp_question_today, '% '], className=color_question_view),
                        html.P('comparado com a média diária', className='card-text d-inline fw-light')], className='d-inline')
                    ], className='card-body')], className='card mx-1 mb-2'),
                html.Div([
                    html.Div('Pesquisas', className='card-header'),
                    html.Div([
                    html.B(format_number_as_thousand(get_total_search())),
                    html.Hr(), 
                    html.P([
                        html.P([html.B('Hoje: '), get_search_today()], className='d-inline'),
                        # html.I(className=question_view_color_symbol + ' ' + color_question_view),
                        # html.B([perc_comp_question_today, '% '], className=color_question_view),
                        # html.P('comparado com a média diária', className='card-text d-inline fw-light')
                        ], className='d-inline')
                    ], className='card-body')], className='card mx-1 mb-2')
                ], className='card-group')
            )
        ),
        ]
        '''

            dbc.Row([
        html.Div(
            dbc.Toast(
                [html.P(html.B(format_number_as_thousand(get_total_access())), className="mb-2")],
                header="Total de acessos",
                style={"width": 150, 'height': 150},
            ), className='lead col-md-2 mb-2'
        ),
        html.Div(
            dbc.Toast(
                [html.P(html.B(format_number_as_thousand(access_last_month())), className="mb-2")],
                header="Acessos no último mês",
                style={"width": 150, 'height': 150},
            ), className='lead col-md-2 mb-2'
        ),
        html.Div(
            dbc.Toast(
                [html.P(html.B(format_number_as_thousand(get_mean_visit_by_bussiness_day_month())), className="mb-2")],
                header="Média mensal de acessos",
                style={"width": 150, 'height': 150},
            ), className='lead col-md-2 mb-2'
        ),
        html.Div(
            dbc.Toast(
                [html.P(html.B(format_number_as_thousand(access_last_month())), className="mb-2"),
                html.Hr(),
                html.P([f'Acessos hoje: ', html.B(format_number_as_thousand(get_visits_today()))])
                ],
                header="Acessos diários",
                style={"width": 150, 'height': 150},
            ), className='lead col-md-2 mb-2'
        ),
        html.Div(
            dbc.Toast(
                [html.P(html.B(format_number_as_thousand(get_visits_today())), className="mb-2")],
                header="Quantidade total de acessos",
                style={"width": 150, 'height': 150},
            ), className='lead col-md-2 mb-2'
        ),
        html.Div(
            dbc.Toast(
                [html.P(html.B(format_number_as_thousand(access_last_month())), className="mb-2")],
                header="Quantidade total de acessos",
                style={"width": 150, 'height': 150},
            ), className='lead col-md-2 mb-2'
        )
        ]),
            html.P([
            f"Já tivemos ",
            html.B(format_number_as_thousand(get_total_access())),
            f" acessos totais!",
            html.Br(),
            html.B(format_number_as_thousand(access_last_month())),
            " acessos no mês passado",
            html.Br(),
            f"A média mensal de acessos é de ", 
            html.B(format_number_as_thousand(get_mean_visit_by_bussiness_day_month())), 
            ", no mês atual tivemos ", html.B(format_number_as_thousand(get_total_visit_by_bussiness_day_in_current_month())),
            ' acessos, que representa ',
            html.B(round((get_total_visit_by_bussiness_day_in_current_month() / get_mean_visit_by_bussiness_day_month()) *100 , 2)),
            '%',
            html.Br(),
            html.B(format_number_as_thousand(get_mean_visit_by_bussiness_day())), f' é a média de acessos diários, hoje alcançamos ', html.B(round((get_visits_today() / get_mean_visit_by_bussiness_day()) * 100, 2)), f'%, totalizando {format_number_as_thousand(get_visits_today())} acessos'
        ], className="lead", id='test'
        ),
            html.Hr(className="my-2"),
            html.P([
                f"Foram ",
                html.B(format_number_as_thousand(get_total_questions_views())),
                f" visualizações de  ",
                html.B(format_number_as_thousand(get_questions_answered())),
                " perguntas respondidas."
            ], id='questions-anwsered'),
            html.Hr(className='my-2'),
            html.P([
                f'E ',
                html.B(format_number_as_thousand(get_total_search())),
                ' pesquisas'
            ], id='searches')
'''

    # @dash_app.callback(
    #     Output('tab_content', 'children'),
    #     [Input('tabs', 'active_tab'),
    #     Input('tabs', 'active_tab'),
    #     Input('tabs', 'active_tab'),
    #     Input('tabs', 'active_tab'),
    #     ],Input('store', 'data'),
    # )
    # def render_tab_content(active_tab, data):
    #     if active_tab and data is None:
    #         if active_tab == 'access_day':
    #             return dcc.Graph(figure=get_graph_access_by_date(), config={'displayModeBar': False})
    #         elif active_tab == 'views_day':
    #             return dcc.Graph(figure=get_questions_views_by_date(), config={'displayModeBar': False})
    #         elif active_tab == 'tags_topics':
    #             return dbc.Row([
    #                 dbc.Col(dcc.Graph(figure=get_graph_tags(), config={'displayModeBar': False})),
    #                 dbc.Col(dcc.Graph(figure=get_graph_topics(), config={'displayModeBar': False})),
    #             ])
    #     return "No tab selected"

    @dash_app.callback(Output('questions-month', 'figure'), [
        Input('checklist', 'value')
    ])
    def update_questions_month(names):
        return get_graph_questions_by_month(names)

    @dash_app.server.route('/dashboard/')
    def dashboard():
        return render_template('dashboard.html', dash=dash_app.index())
    return dash_app.server













## Visistas ultimo mês
# lastmonth = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
# Visit.query.filter(or_(Visit.user_id == 4, Visit.user_id == None),extract('isodow', Visit.datetime) < 7, Visit.datetime <= lastmonth).count()

# db.session.query(Question).filter(
#     Question.answer_approved_at <= lastmonth,
#     Question.answer_approved== True).count()