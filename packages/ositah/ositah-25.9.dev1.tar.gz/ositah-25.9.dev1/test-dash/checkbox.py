import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import MATCH, Input, Output, State

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

standalone_radio_check = html.Div(
    [
        dbc.Form(
            [
                dbc.FormGroup(
                    [
                        dbc.Checkbox(
                            id={"type": "standalone", "id": 1},
                            className="form-check-input",
                        ),
                        dbc.Label(
                            "This is a checkbox",
                            html_for="standalone-checkbox",
                            className="form-check-label",
                        ),
                        html.P(id={"type": "check-output", "id": 1}),
                    ],
                    check=True,
                ),
                dbc.FormGroup(
                    [
                        dbc.RadioButton(
                            id={"type": "standalone", "id": 2},
                            className="form-check-input",
                        ),
                        dbc.Label(
                            "This is a radio button",
                            html_for="standalone-radio",
                            className="form-check-label",
                        ),
                        html.P(id={"type": "check-output", "id": 2}),
                    ],
                    check=True,
                ),
            ]
        ),
    ]
)


@app.callback(
    Output({"type": "check-output", "id": MATCH}, "children"),
    Input({"type": "standalone", "id": MATCH}, "value"),
    State({"type": "standalone", "id": MATCH}, "id"),
)
def on_form_change(box_checked, id):
    # print('callback entered')
    if box_checked:
        return f"Checkbox {id['id']} checked."
    else:
        return f"Checkbox {id['id']} unchecked."


app.layout = standalone_radio_check

if __name__ == "__main__":
    app.run_server(debug=True)
