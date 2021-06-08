from flask import url_for
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html

import dash_bootstrap_components as dbc

def dash_app(app=False):
    dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.BOOTSTRAP])

    with dash_app.server.app_context():
        print(url_for('main.index', _external=False))

    dash_app.layout = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand=app.config.get('PROJECT_NAME', False),
    brand_href="#",
    color="primary",
    dark=True,
)


    return dash_app.server