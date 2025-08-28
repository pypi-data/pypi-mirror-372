import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import MATCH, Input, Output, State

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


def create_switches(number):
    if number == 0:
        return ""
    return html.Div(
        [
            dbc.Form(
                [
                    dbc.Label(
                        "This is a group of switches",
                        html_for="standalone-checkbox",
                        className="form-check-label",
                    ),
                    dbc.FormGroup(
                        [
                            dbc.FormGroup(
                                [
                                    dbc.Checklist(
                                        options=[
                                            {"label": f"Test switch {i}", "value": i},
                                            {
                                                "label": f"Test switch {i}bis",
                                                "value": i * 100,
                                            },
                                        ],
                                        id={"type": "switch", "id": i},
                                        value=[],
                                        switch=True,
                                    ),
                                    html.Div(id={"type": "check-output", "id": i}),
                                ]
                            )
                            for i in range(1, number + 1)
                        ],
                        check=True,
                    ),
                ]
            )
        ]
    )


def create_jumbotron(error_msg):
    return dbc.Jumbotron(
        [html.H1("Unexpected error in switch callback"), html.P(error_msg)]
    )


@app.callback(
    Output({"type": "check-output", "id": MATCH}, "children"),
    Input({"type": "switch", "id": MATCH}, "value"),
    State({"type": "switch", "id": MATCH}, "id"),
    prevent_initial_call=True,
)
def on_form_change(values, id):
    # print('callback entered')
    if len(values) == 0:
        return f"Switch {id['id']} state: off"
    elif len(values) <= 2:
        switches_on = []
        for v in values:
            if v == id["id"]:
                switches_on.append(str(id["id"]))
            elif v == 100 * id["id"]:
                switches_on.append(str(f"{id['id']}bis"))
            else:
                return create_jumbotron(
                    f"Unexpected switch ID/value (received: {values[0]}, expected: {id['id']})"
                )

        return f"Switch {' and '.join(switches_on)} state: on"

    else:
        return create_jumbotron(f"Unexpected number of values received ({len(values)})")


app.layout = html.Div(
    [
        dbc.Input(
            id="num_rows", placeholder="Number of switches to create", type="int"
        ),
        html.Div(id="num_rows_txt"),
        html.Br(),
        html.Div(id="switches"),
    ]
)


@app.callback(
    [
        Output("num_rows_txt", "children"),
        Output("switches", "children"),
    ],
    Input("num_rows", "value"),
)
def create_switch_button(value):
    if value is None:
        value = 0
    else:
        value = int(value)
    switches = create_switches(value)
    return f"Number of switches to create: {value}", switches


if __name__ == "__main__":
    app.run_server(debug=True)
