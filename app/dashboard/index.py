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

import dash_bootstrap_components as dbc
from flask.templating import render_template
import plotly.express as px
import pandas as pd
from app.models.wiki import Question, Topic, Tag, QuestionView
from app.core.db import db
from sqlalchemy import func, asc, inspect

def get_graph_tags():
    df = pd.read_sql(db.session.query(Tag.name.label('Marcação'), func.count(Question.id).label('Total')).outerjoin(Question.tags).group_by(Tag).statement, con=db.session.bind)
    df['Marcação'].replace({None:'Vazio'}, inplace=True)
    graph = px.pie(df, values='Total', names='Marcação', title= 'Marcações')
    return graph

def get_graph_topics():
    df = pd.read_sql(db.session.query(Topic.name.label('Nome'), Topic.selectable.label('Selecionável'), func.count(Question.id).label('Total')).outerjoin(Question).group_by(Topic).statement, con=db.session.bind)
    graph = px.pie(df, values='Total', names='Nome', title='Tópicos')
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
            f" perguntas visualizadas, de ",
            html.B(get_questions_answered()),
            " perguntas respondidas."
        ]),
        # html.P(dbc.Button("Learn more", color="primary"), className="lead"),
    ], className='p-3'
),
            dbc.Tabs([
                dbc.Tab(label='Acessos por dia', tab_id='access_day'),
                dbc.Tab(label='Questões vistas por dia', tab_id='views_day'),
                dbc.Tab(label='Perguntas por tópicos e tags', tab_id='tags_topics')
            ], id='tabs',
            active_tab='access_day'),
            html.Div(id='tab_content', className='p-4'),

        #     dbc.Tabs([
        #         dbc.Tab(label='Teste', tab_id='outro_teste',
        #         children=[]),
        #         dbc.Tab(label='Teste1', tab_id='outro_teste1'),
        #         dbc.Tab(label='Teste2', tab_id='outro_teste2'),], 
        #         id='tabs1',
        #         active_tab='outro_teste'),
        
        #     dcc.Tabs(id="tabs2", value='tab1', children=[
        #     dcc.Tab(label='Tab One', value='tab13', id='teste',
        #             children=[dcc.Tabs(id="subtabs", value="subtab1",
        #                 children = [dcc.Tab(label='Sub Tab1', value="subtabs1", children=[]),
        #                 dcc.Tab(label='Sub Tab2', value="subtab2", children=[])])]),
        #     dcc.Tab(label='Tab Two', value='tab2', children=[]),
        #     dcc.Tab(label='Tab Three', value='tab3', children=[]),
        # ]),
        # html.Div(id='tabs-content'),
        # html.Br(),
        # html.Br(),
        # html.Br(),
        # html.Br(),
        # html.Br(),

        ])
    # @dash_app.callback(
    #     Output('tabs-content', 'chil'),
    #     Input('subtabs', 'value')
    # )
    # def teste_render2(value):
    #     print(value)
    # @dash_app.callback(
    #     Output('tabs-content', 'chil'),
    #     [Input('tabs2', 'value')]
    # )
    # def teste_render(value):
    #     print(value)

    @dash_app.callback(
        Output('tab_content', 'children'),
        Input('tabs', 'active_tab'), Input('store', 'data'),
    )
    def render_tab_content(active_tab, data):
        if active_tab and data is None:
            if active_tab == 'access_day':
                return dcc.Graph(figure=get_graph_access_by_date(), config={'displayModeBar': False})
            elif active_tab == 'views_day':
                return dcc.Graph(figure=get_questions_views_by_date(), config={'displayModeBar': False})
            elif active_tab == 'tags_topics':
                return dbc.Row([
                    dbc.Col(dcc.Graph(figure=get_graph_tags(), config={'displayModeBar': False})),
                    dbc.Col(dcc.Graph(figure=get_graph_topics(), config={'displayModeBar': False})),
                ])
        return "No tab selected"

    @dash_app.callback(Output('questions-month', 'figure'), [
        Input('checklist', 'value')
    ])
    def update_questions_month(names):
        return get_graph_questions_by_month(names)

    @dash_app.server.route('/dashboard/')
    def dashboard():
        return render_template('dashboard.html', dash=dash_app.index())
    return dash_app.server