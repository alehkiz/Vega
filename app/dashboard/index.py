from unicodedata import category
from dash_bootstrap_components._components.Alert import Alert
from dash_html_components.B import B
from dash_html_components.Br import Br
from sqlalchemy.sql.expression import label
from app.models.app import Visit
from re import template
from dash_core_components.Checklist import Checklist
# from flask import config, url_for, app as current_app
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table import DataTable

import dash_bootstrap_components as dbc
from flask.templating import render_template
import plotly.express as px
import pandas as pd
from app.models.wiki import Question, SubTopic, Topic, Tag, QuestionView
from app.core.db import db
from sqlalchemy import func, asc, inspect

def get_graph_tags():
    df = pd.read_sql(db.session.query(Tag.name.label('Marcação'), func.count(Question.id).label('Total')).outerjoin(Question.tags).group_by(Tag).statement, con=db.session.bind)
    df['Marcação'].replace({None:'Vazio'}, inplace=True)
    graph = px.pie(df, values='Total', names='Marcação', title= 'Marcações')
    return graph

def get_graph_topics():
    df = pd.read_sql(db.session.query(Topic.name.label('Nome'), Topic.selectable.label('Selecionável'), func.count(Question.id).label('Total')).filter(Topic.selectable == True, Topic.active == True).outerjoin(Question).group_by(Topic).statement, con=db.session.bind)
    graph = px.pie(df, values='Total', names='Nome', title='Tópicos')
    return graph

def get_graph_sub_topics():
    df = pd.read_sql(db.session.query(SubTopic.name.label('Nome'), func.count(Question.id).label('Total')).outerjoin(Question).group_by(SubTopic).statement, con=db.session.bind)
    graph = px.pie(df, values='Total', names='Nome', title='Sub-Tópicos')
    return graph

def get_graph_questions_by_month(names=None):
    df = pd.read_sql(db.session.query(func.count(Question.id).label('Total'), 
        func.date_trunc('month', Question.create_at).label('Mês'), Topic.name.label('Assunto')
        ).join(Topic.questions).group_by('Mês', 'Assunto').order_by(asc('Mês')
        ).statement, db.session.bind)
    if df.empty is True:
        df.Total = pd.Series([0])
        df.at[0, 'Mês'] = None
        df.at[0, 'Assunto'] = ' '
    if names == None:
        return px.line(df, x = 'Mês', y = 'Total', title='Dúvidas cadastradas por dia e assunto', color='Assunto', hover_data={'Mês': "|%m/%Y"})
    mask = df.Assunto.isin(names)
    graph = px.line(df[mask], x = 'Mês', y = 'Total', title='Dúvidas cadastradas por dia e assunto', color='Assunto', hover_data={'Mês': "|%m/%Y"})
    return graph

def get_questions_views_by_date():
    df = pd.read_sql(
        db.session.query(func.count(QuestionView.id).label('Total'), func.date_trunc('day', QuestionView.datetime).label('Data')).group_by('Data').order_by(asc('Data')).statement, con=db.session.bind)
    graph = px.line(df, x = 'Data', y= 'Total', title='Perguntas visualizadas por dia')
    return graph

def get_graph_questions_answers_by_date():
    df = pd.read_sql(
        db.session.query(func.count(Question.id).label('Total'), func.date_trunc('day', Question.answer_at).label('Data')).filter(Question.answer != None).group_by('Data').order_by(asc('Data')).statement, con=db.session.bind)
    graph = px.line(df, x = 'Data', y= 'Total', title='Respostas por dia')
    return graph

def get_graph_access_by_date():
    df = pd.read_sql(db.session.query(func.count(Visit.id).label('Total'), 
                func.date_trunc('day', Visit.datetime).label('Data')).group_by('Data').order_by(
                    asc('Data')).statement, con=db.session.bind)
    graph = px.line(df, x = 'Data', y= 'Total', title='Acessos por dia')
    return graph

def get_total_access():
    return Visit.query.count()

def get_total_questions_views():
    return QuestionView.query.count()
def get_questions_answered():
    return Question.query.filter(Question.active == True, Question.answer != '', Question.answer_approved==True).count()

def dash_app(app=False):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashapp/', external_stylesheets=[dbc.themes.BOOTSTRAP], update_title='Atualizando...')
    
    engine = db.get_engine(app)
    if not inspect(engine).dialect.has_table(engine.connect(), table_name = 'topic'):
        dash_app.layout = html.Div()
    else:
        topics = [x.name for x in Topic.query]
        dash_app.layout = dbc.Container([
            dcc.Store(id='store'),
            dbc.Jumbotron(
    [
        html.H1("Dashboard AtenDetran", className="display-5"),
        html.P([
            f"Já tivemos ", 
            html.B(get_total_access()),
            " acessos!",
            html.Br(),
            ],
            className="lead",
        ),
        html.Hr(className="my-2"),
        html.P([
            f"Foram ",
            html.B(get_total_questions_views()),
            f" visualizações de  ",
            html.B(get_questions_answered()),
            " perguntas respondidas."
        ]),
        # html.P(dbc.Button("Learn more", color="primary"), className="lead"),
    ], className='p-3'
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
                        dbc.Tab(label='Visualizações de perguntas', tab_id='diary-questions-views'),
                        dbc.Tab(label='Perguntas e Respostas', tab_id='diary-questions-answers'),
                        # dbc.Tab(label='', tab_id='diary-'),
                    ], id='diary-tab', active_tab='diary-access')]),
                dbc.Tab(label='Comparativos percentuais', tab_id='percent', children=[
                    dbc.Tabs([
                        dbc.Tab(label='Marcações', tab_id='percent-tags'),
                        dbc.Tab(label='Tópicos', tab_id='percent-topics'),
                        dbc.Tab(label='Sub-Tópicos', tab_id='percent-sub-topics'),
                    ], id='percent-tab', active_tab='percent-tags')]),
                dbc.Tab(label='Top respostas', tab_id='user', children=[
                    dbc.Tabs([
                        dbc.Tab(label='Respostas', tab_id='user-answers'),
                        dbc.Tab(label='Aprovações', tab_id='user-approve')
                    ], id='user-tab', active_tab='user-answers')]),
                ], id='tabs', active_tab='diary'),
                html.Div(id='tab_content', className='p-4'),
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
        print(tab, params)
        if len(active_subtab) == 1:
            active_subtab = active_subtab[0]
            print(active_subtab)
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
                return 'answers'
            elif active_subtab == 'user-approve':
                return 'approve'
        else:
            return 'Nenhuma seleção'

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