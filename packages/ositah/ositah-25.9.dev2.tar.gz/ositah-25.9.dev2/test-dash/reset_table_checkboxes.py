#!/usr/bin/env python

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

app.layout = html.Div(
    [
        dbc.Input(
            id="num_rows", placeholder="Number of switches to create", type="int"
        ),
        html.Div(id="num-selected"),
        html.P(),
        html.Div(id="table-div-id"),
        dcc.Store(id="selection-update-status"),
    ]
)


@app.callback(
    Output("table-div-id", "children"),
    Input("num_rows", "value"),
    prevent_initial_call=True,
)
def create_table(num_rows):
    table_header = [
        html.Thead(
            html.Tr(
                [
                    html.Th(dbc.Checkbox(id="checkbox-all")),
                    html.Th("Value"),
                    dcc.Store(id="all-selected", data=0),
                ]
            )
        )
    ]

    table_body = [
        html.Tbody(
            [
                html.Tr(
                    [
                        html.Td(
                            dbc.Checkbox(
                                {"type": "checkbox", "id": i},
                                className="table-checkbox",
                            )
                        ),
                        html.Td(f"Texte {i}"),
                    ]
                )
                for i in range(int(num_rows))
            ]
        )
    ]

    return dbc.Table(table_header + table_body, bordered=True, striped=True)


@app.callback(
    Output("num-selected", "children"),
    Input("checkbox-all", "value"),
    State("num_rows", "value"),
)
def select_all(checked, num_selected):
    if checked:
        return f"{num_selected} selected"
    else:
        return ""


app.clientside_callback(
    """
    function define_checkbox_status(checked) {
        console.log('define_checkbox_status entered with checked='+checked);
        const checkbox_forms = document.querySelectorAll(".table-checkbox");
        checkbox_forms.forEach(function(cb_form) {
            const cb = cb_form.querySelector("input");
            console.log("Updating checkbox "+cb.id);
            if ( checked ) {
                cb.checked = true;
            } else {
                cb.checked = false;
            }
        });
        return checked;
    }
    """,
    Output("selection-update-status", "data"),
    Input("checkbox-all", "value"),
    prevent_initial_call=True,
)


app.run_server(debug=True)
