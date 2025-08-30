from dash import Dash, dcc, Input, Output, html
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO


dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
)
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

df = px.data.tips()

color_mode_switch =  html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="switch"),
        dbc.Switch( id="switch", value=True, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="switch"),
    ]
)

app.layout = dbc.Container(
    [
        ThemeSwitchAIO(aio_id="theme", themes=[dbc.themes.FLATLY]),
        # color_mode_switch,
        dcc.Dropdown(
            id="values",
            value="total_bill",
            options=[{"value": x, "label": x} for x in ["total_bill", "tip", "size"]],
            clearable=False,
        ),
        dcc.Graph(id="pie-chart"),
    ],
    fluid=True,
    className="dbc",
)


@app.callback(
    Output("pie-chart", "figure"),
    Input("values", "value"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
    # Input("color-mode-switch", "value",)
)
def generate_chart(value, toggle):
    template = "flatly" if toggle else "flatly-dark"
    fig = px.pie(df, values=value, names="day", template=template)
    return fig


if __name__ == "__main__":
    app.run(debug=True)
