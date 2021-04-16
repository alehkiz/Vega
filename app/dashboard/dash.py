from app.models.search import Search
from flask import current_app as app, Blueprint, render_template, url_for, redirect, flash, json, Markup, g, abort, request
from flask_security import login_required, current_user
from datetime import datetime

from app.core.db import db
from app.models.wiki import Article, Question, Tag, Topic

from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
# import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

def dash_appication(app):

    dash_app = Dash(__name__, 
                    server=app, # Don't give dash a server just yet.
                    url_base_pathname='/dashboard/', external_stylesheets=external_stylesheets)

    df = pd.DataFrame({
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    })


    # fig.update_layout(
    #     plot_bgcolor=colors['background'],
    #     paper_bgcolor=colors['background'],
    #     font_color=colors['text']
    # )

    dash_app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H1(
            children='Hello Dash',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.Div(children='Dash: A web application framework for Python.', style={
            'textAlign': 'center',
            'color': colors['text']
        }),
        dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }, 
        config={
        'displayModeBar': False
    }
    )
    ])
    return dash_app.server