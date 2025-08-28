#!/usr/bin/env python
#
# Progess bar associated with a callback using the long running callback feature, as provided
# in Dash 2.0. The "running" actions are used to start the progress bar as part of the
# callback doing the real work.

from tempfile import mkdtemp
from time import sleep

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.long_callback import DiskcacheLongCallbackManager
from diskcache import Cache

cache_dir = mkdtemp(dir="/tmp")
cache = Cache(cache_dir)
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    long_callback_manager=long_callback_manager,
)

INTERVAL_DURATION = 500
MAX_INTERVAL = 30

app.layout = html.Div(
    [
        html.Div(id="callback-output"),
        html.Div(
            [
                html.Div(id="status-bar"),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Progress(id="progress", striped=True),
                            width=5,
                        ),
                        dbc.Col(
                            dbc.Button("Cancel", id="stop-workload"),
                            width=1,
                        ),
                    ],
                    align="center",
                ),
            ],
            id="progress-row",
            style={"visibility": "hidden"},
        ),
        dcc.Interval(
            id="progress-interval",
            max_intervals=0,
            n_intervals=0,
            interval=INTERVAL_DURATION,
        ),
        dbc.Button("Start progess bar", id="start-workload", className="mt-3"),
        dcc.Store(id="start-progress-bar", data=0),
        dcc.Store(id="start-progress-bar-saved", data=0),
    ],
    id="status-info",
)


@app.callback(
    [Output("progress", "value"), Output("progress", "label")],
    [Input("progress-interval", "n_intervals")],
    prevent_initial_call=True,
)
def update_progress(n):
    # print(f"update_progress: n={n}")
    progress = int(round(n / MAX_INTERVAL * 100))
    # only add text after 5% progress to ensure text isn't squashed too much
    return progress, f"{progress} %" if progress >= 5 else ""


@app.long_callback(
    Output("callback-output", component_property="children"),
    Input("start-workload", "n_clicks"),
    running=[
        (Output("start-workload", "disabled"), True, False),
        (Output("status-bar", "children"), "Callback started", ""),
        (
            Output("progress-row", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
        (Output("start-progress-bar", "data"), 1, 0),
    ],
    cancel=[Input("stop-workload", "n_clicks")],
    prevent_initial_call=True,
)
def execute_work(n):
    if n:
        print("Starting progress bar", flush=True)
        sleep(MAX_INTERVAL * INTERVAL_DURATION / 1000)
        return html.P("Done")
    else:
        raise PreventUpdate


@app.callback(
    Output("progress-interval", "n_intervals"),
    Output("progress-interval", "max_intervals"),
    Output("start-progress-bar-saved", "data"),
    Input("start-progress-bar", "data"),
    State("start-progress-bar-saved", "data"),
    prevent_initial_call=True,
)
def start_progress_bar(start, previous_start):
    # For some reasons, the callback is called multiple times, probably because the input
    # value is set as part of the "running" property of the long-running callback. To avoid
    # resetting the progress bar, keep track of the previous value.
    # print(f"start={start}, start.saved={previous_start}")
    if start != previous_start:
        if start:
            max_interval = MAX_INTERVAL
        else:
            max_interval = 0
        return 0, max_interval, start
    else:
        raise PreventUpdate


if __name__ == "__main__":
    app.run_server(debug=True)
