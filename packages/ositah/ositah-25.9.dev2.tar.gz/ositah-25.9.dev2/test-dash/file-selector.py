#!/usr/bin/env python
# Example from DCC documentation about dcc.Download

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(prevent_initial_callbacks=True)
app.layout = html.Div(
    [html.Button("Download Text", id="btn_txt"), dcc.Download(id="download-text")]
)


@app.callback(
    Output("download-text", "data"),
    Input("btn_txt", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dict(content="Hello world!", filename="hello.txt")


if __name__ == "__main__":
    app.run_server(debug=True)
