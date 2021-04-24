from app.models.search import Search
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, g, abort, request, has_app_context, appcontext_pushed
from flask_security import login_required, current_user
from datetime import datetime

from app.core.db import db
from app.models.wiki import Article, Question, Tag, Topic

from dash import Dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from bs4 import BeautifulSoup


# import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

def dash_appication(app=False):

    dash_app = Dash(__name__, 
                    server=app, # Don't give dash a server just yet.
                    url_base_pathname='/dash_app/', external_stylesheets=[dbc.themes.BOOTSTRAP])
    # if has_app_context():
    with dash_app.server.app_context():
        df = pd.read_sql_table('question_view', db.session.connection())
        df['date'] = df.datetime.dt.date#.strftime("%d/%m/%Y")
        df = df.groupby(['date'], as_index=False).agg({'id':'count'})


        # fig.update_layout(
        #     plot_bgcolor=colors['background'],
        #     paper_bgcolor=colors['background'],
        #     font_color=colors['text']
        # )

        dash_app.layout = html.Div(
            style={'backgroundColor': colors['background']}, children=[
            # html.H1(
            #     children='Relatório de serviços',
            #     style={
            #         'textAlign': 'center',
            #         'color': colors['text']
            #     }
            # ),

            # html.Div(children=f'Relatório de: 2020', style={
            #     'textAlign': 'center',
            #     'color': colors['text']
            # }),
            dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {
                        'x': df['date'], 
                        'y': df['id'], 
                        'type': 'scatter', 
                        'mode': 'lines',
                        'name': 'Habilitação',
                        'line':dict(
                            shape="spline",
                            smoothing="2",
                            color='#F9ADA0'
                        )},
                    # {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Veículos'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization',
                    'xaxis': {
                        'tickformat': '%m/%y'
                    }
                }
            }, 
            config={
            'displayModeBar': False,
            'locale': 'pt_BR'
        }
        )
        ])

        dash_app.layout = dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {
                        'x': df['date'], 
                        'y': df['id'], 
                        'type': 'scatter', 
                        'mode': 'lines',
                        'name': 'Habilitação',
                        'line':dict(
                            shape="spline",
                            smoothing="2",
                            color='#F9ADA0'
                        )},
                    # {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Veículos'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization',
                    'xaxis': {
                        'tickformat': '%m/%y'
                    }
                }
            }, 
            config={
            'displayModeBar': False,
            'locale': 'pt_BR'
        }
        )
    return dash_app