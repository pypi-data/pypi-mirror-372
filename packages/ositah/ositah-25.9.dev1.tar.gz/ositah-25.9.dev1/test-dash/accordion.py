#!/usr/bin/env python

import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import MATCH, Input, Output, State

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def make_item(i):
    # we use this function to make the example items to avoid code duplication
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"Collapsible group #{i}",
                        color="link",
                        id={"type": "accordion-toggle", "id": i},
                    )
                )
            ),
            dbc.Collapse(
                dbc.CardBody(f"This is the content of group {i}..."),
                id={"type": "accordion-collapse", "id": i},
            ),
        ]
    )


@app.callback(
    Output({"type": "accordion-collapse", "id": MATCH}, "is_open"),
    Input({"type": "accordion-toggle", "id": MATCH}, "n_clicks"),
    State({"type": "accordion-collapse", "id": MATCH}, "is_open"),
)
def toggle_agent(n_clicks: int, state: bool) -> bool:
    """
    Callback function for the accordions attached to the agents. For each click, the state
    (open/closed) is changed. The index is used to match the input and the output.

    :param n_clicks: non-zero if the accordion link was clicked
    :param state: the current state of the accordion
    :return: the new state of the corresponding collapse
    """

    print("callback entered")
    if n_clicks:
        return not state
    else:
        return state


def create_accordion(button_to_init):
    accordion = html.Div(
        dbc.Table(
            [
                html.Thead(html.Tr([html.Th("Agent"), html.Th("Validation")])),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(make_item(i), className="accordion"),
                                html.Td("Validated?"),
                            ]
                        )
                        for i in range(1, button_to_init + 1)
                    ]
                ),
            ]
        )
    )

    return accordion


app.layout = html.Div(
    [
        dbc.Input(
            id="num_rows",
            placeholder="Number of table rows",
            min=1,
            max=100,
            step=1,
            type="number",
        ),
        html.Br(),
        html.P(id="output"),
        html.Div(id="table"),
    ]
)


@app.callback(
    [Output("output", "children"), Output("table", "children")],
    [Input("num_rows", "value")],
)
def output_text(value):
    if value is None or value == "":
        value = 0
    return f"Number of rows created: {value}", create_accordion(int(value))


if __name__ == "__main__":
    app.run_server(debug=True)
