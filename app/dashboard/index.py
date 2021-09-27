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
from app.models.wiki import Question, Topic, Tag
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

def get_graph_access_by_date():
    df = pd.read_sql(db.session.query(func.count(Visit.id).label('Total'), 
                func.date_trunc('day', Visit.datetime).label('Data')).group_by('Data').order_by(
                    asc('Data')).statement, con=db.session.bind)
    graph = px.line(df, x = 'Data', y= 'Total', title='Acessos por dia')
    return graph

def dash_app(app=False):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashapp/', external_stylesheets=[dbc.themes.BOOTSTRAP], update_title='Atualizando...')
    
    engine = db.get_engine(app)
    if not inspect(engine).dialect.has_table(engine.connect(), table_name = 'topic'):
        dash_app.layout = html.Div()
    else:
        topics = [x.name for x in Topic.query]

        dash_app.layout = html.Div(children=[
        html.H1(children='Dashboard'),
        html.Div([
            html.H4(children='Acessos'),
            html.Div([
                dcc.Graph(id='access', figure=get_graph_access_by_date(), config={
            'displayModeBar': False
        })], className='col-sm'),
            
        ]),

        html.Div([
            html.H4(children='Questões cadastradas'),
            html.Div([dcc.Graph(id='topics', figure=get_graph_topics(), config={
            'displayModeBar': False
        })], className='col-sm'),
            html.Div([dcc.Graph(id='tags', figure=get_graph_tags(), config={
                'displayModeBar': False
            }    
        )
            ], className='col-sm'),
            dcc.Checklist(
                id='checklist', 
                options=[{'label': x, 'value': x} for x in topics],
                value=topics,
                labelStyle={'display': 'inline-block'}
            ),
            
            html.Div([dcc.Graph(id='questions-month', figure=get_graph_questions_by_month(), config={
                    'displayModeBar': False
                })
            ])
        ], className='row')
        ])

    @dash_app.server.route('/dashboard/')
    def dashboard():
        
        return render_template('dashboard.html', dash=dash_app.index())
    # print(dash_app.index())
    

    @dash_app.callback(Output('questions-month', 'figure'), [
        Input('checklist', 'value')
    ])
    def update_questions_month(names):
        return get_graph_questions_by_month(names)

    return dash_app.server