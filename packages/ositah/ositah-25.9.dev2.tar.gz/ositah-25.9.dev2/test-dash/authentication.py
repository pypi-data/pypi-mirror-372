#!/usr/bin/env python
#
# Application to test using flask-multipass from Dash to authenticate through LDAP

import argparse
import os
import sys

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from flask import Flask

# Add to Python path the apps module which resides at the same level as this script parent dir
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from utils.authentication import (  # noqa: E402
    configure_multipass_ldap,
    multipass,
    protect_views,
)
from utils.utils import define_config_params  # noqa: E402

app = Dash(
    "__name__", external_stylesheets=[dbc.themes.BOOTSTRAP], server=Flask(__name__)
)

SIDEBAR_WIDTH = 16
SIDEBAR_HREF_VALIDATION = "/validation"
SIDEBAR_HREF_NSIP_EXPORT = "/nsip"

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": f"{SIDEBAR_WIDTH}rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H2("OSITAH", className="display-4"),
        html.Hr(),
        html.P("Suivi des déclarations de temps", className="lead"),
        dbc.Nav(
            [
                # external_link=True added otherwise the callback was not called... not clear why...
                dbc.NavLink("Home", href="/", active="exact", external_link=True),
                dbc.NavLink(
                    "Validation",
                    href=SIDEBAR_HREF_VALIDATION,
                    active="exact",
                    external_link=True,
                ),
                dbc.NavLink(
                    "Export NSIP",
                    href=SIDEBAR_HREF_NSIP_EXPORT,
                    active="exact",
                    external_link=True,
                ),
            ],
            vertical="md",
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": f"{SIDEBAR_WIDTH+2}rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("Sélectionner ce que vous souhaitez faire")
    elif pathname == SIDEBAR_HREF_VALIDATION:
        return define_validation_layout()
    elif pathname == SIDEBAR_HREF_NSIP_EXPORT:
        return html.P("Not yet implemented")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"URL {pathname} was not recognised..."),
        ]
    )


def define_validation_layout():
    """
    Build the layout for this application, after reading the data if necessary.

    :return: application layout
    """

    return html.Div(
        [
            html.H1("Validation des déclarations de temps par les agents"),
            # team_list_dropdown(global_params.project_declarations),
            html.Div(id="teams-display-value"),
            html.Div(id="declaration_table", style={"margin-top": "3em"}),
        ]
    )


def main():
    # Default config file is 'ositash.cfg' in the parent directory
    config_file_default = (
        f"{os.path.dirname(os.path.dirname(__file__))}/ositah.example.cfg"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--configuration-file",
        default=config_file_default,
        help=f"Configuration file (D: {config_file_default}",
    )
    options = parser.parse_args()

    _ = define_config_params(options.configuration_file)

    configure_multipass_ldap(app.server, "IJCLab Active Directory")
    multipass.init_app(app.server)

    app.server.secret_key = "fma-example"

    protect_views(app)

    app.run_server(debug=True)


if __name__ == "__main__":
    main()
