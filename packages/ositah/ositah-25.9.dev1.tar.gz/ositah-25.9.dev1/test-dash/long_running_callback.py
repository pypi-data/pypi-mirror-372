#!/usr/bin/env python
#
# Example of a long running callback, as provided in Dash 2.0. The real work must be done in a
# separate process/thread started by the callback and the progress function can be called
# regularly inside the callback to update the progress information.
# Based on example provided in Dash documentation, https://dash.plotly.com/long-callbacks but
# using Dash Bootstrap Components

import time
from tempfile import mkdtemp

import dash
import dash_bootstrap_components as dbc
import diskcache
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash.long_callback import DiskcacheLongCallbackManager

cache_dir = mkdtemp(dir="/tmp")
cache = diskcache.Cache(cache_dir)
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = dash.Dash(
    __name__,
    long_callback_manager=long_callback_manager,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
)

app.layout = html.Div(
    [
        html.Div(
            [
                html.P(id="paragraph_id", children=["Button not clicked"]),
                dbc.Progress(id="progress_bar", style={"visibility": "hidden"}),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(id="button_id", children="Run Job!"),
                    width={"offset": 1, "size": 1},
                ),
                dbc.Col(
                    dbc.Button(id="cancel_button_id", children="Cancel Running Job!"),
                    width=2,
                ),
            ]
        ),
    ]
)


@app.long_callback(
    output=Output("paragraph_id", "children"),
    inputs=Input("button_id", "n_clicks"),
    running=[
        (Output("button_id", "disabled"), True, False),
        (Output("cancel_button_id", "disabled"), False, True),
        (
            Output("paragraph_id", "style"),
            {"visibility": "hidden"},
            {"visibility": "visible"},
        ),
        (
            Output("progress_bar", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    cancel=[Input("cancel_button_id", "n_clicks")],
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
    prevent_initial_call=True,
)
def callback(set_progress, n_clicks):
    if n_clicks:
        total = 10
        for i in range(total):
            set_progress((str(i + 1), str(total)))
            time.sleep(0.5)
        return [f"Clicked {n_clicks} times"]
    else:
        raise PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True)
