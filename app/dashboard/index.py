from re import template
from flask import config, url_for
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html

import dash_bootstrap_components as dbc
from flask.templating import render_template
import plotly.express as px
import pandas as pd
from app.models.wiki import Question, Topic, Tag
from app.core.db import db
from sqlalchemy import func

def dash_app(app=False):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashapp/', external_stylesheets=[dbc.themes.BOOTSTRAP], update_title='Atualizando...')
    # print(dash_app.serve_layout)

    # fig.show()
    df_tags = pd.read_sql(db.session.query(Tag.name, func.count(Question.id)).outerjoin(Question.tags).group_by(Tag).statement, con=db.session.bind)
    df_tags.rename({'name': 'Marcação', 'count_1':'Total'}, axis=1, inplace=True)
    df_tags['Marcação'].replace({None:'Vazio'}, inplace=True)
    df_topics = pd.read_sql(db.session.query(Topic, func.count(Question.id)).outerjoin(Question).group_by(Topic).statement, con=db.session.bind)
    df_topics.rename({'count_1': 'Total', '_name': 'Tópico'}, axis=1, inplace=True)
    dash_app.layout = html.Div(children=[
    html.H1(children='Dashboard'),

    html.Div([
        html.Div([
        html.Div([html.H3('Tópicos'),
        dcc.Graph(id='topics', figure=px.pie(df_topics,
        values='Total', names='Tópico'), config={
        'displayModeBar': False
    })], className='col-sm'),
        html.Div([
            html.H3('Marcações'),
        dcc.Graph(id='tags', figure=px.pie(df_tags,
        values='Total', names='Marcação'), config={
            'displayModeBar': False
        }    
    )
        ], className='col-sm')
    ], className='row')
    ])
    ])
#     html.Div(children='''
#         Quantidade por tópicos
#     '''),
#     html.Div(children=dcc.Graph(id='topics', figure=px.pie(df_topics,
#         values='Total', names='Tópico'), config={
#         'displayModeBar': False
#     })),
#     html.Div(children='Quantidade de marcações'),
#     html.Div(children=dcc.Graph(id='Marcações', figure=px.pie(df_tags,
#         values='Total', names='Marcação'), config={
#             'displayModeBar': False
#         }    
#     ))
# ])

    

    @dash_app.server.route('/dashboard/')
    def dashboard():
        
        return render_template('dashboard.html', dash=dash_app.index())
    # print(dash_app.index())
    return dash_app.server