# Dash imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Plotly imports
import plotly.graph_objs as go

# Own modules imports
from alphavantage.utils import curr_time, next_update_time

# Other imports
import pandas as pd
import os


CLOCK_STYLE = {
    "display": "inline-block",
    "width": "14%",
    "fontSize": "16px",
    "padding": "5px",
    "textAlign": "center"
}

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    # Local time clock
    html.Div([
        html.Div("Local time"), html.Div(id="live-clock-local"),
        html.Div("Next update at"), html.Div(id="live-next-update-local")
    ], style=CLOCK_STYLE),

    # Gouda Praga
    html.H3("🔥 Gouda Praga 🔥", style={"width": "69%", "display": "inline-block", "textAlign": "center"}),

    # Stock market time clock
    html.Div([
        html.Div("Stock market time"), html.Div(id="live-clock-us"),
        html.Div("Next update at"), html.Div(id="live-next-update-us")
    ], style=CLOCK_STYLE),

    # Plot
    dcc.Graph(id="live-plot"),
        
    # Defining intervals (in milliseconds)
    dcc.Interval(id='interval-clock', n_intervals=0, interval=1000*1),
    dcc.Interval(id='interval-plot', n_intervals=0, interval=1000*5)
])


# -----------------------------------------------------
# -------------------- Local clock --------------------
# -----------------------------------------------------
@app.callback(Output("live-clock-local", "children"), [Input("interval-clock", "n_intervals")])
def live_clock_local(n):
    return html.Span(curr_time(output_format="%H:%M:%S"))


@app.callback(Output("live-next-update-local", "children"), [Input("interval-clock", "n_intervals")])
def live_next_update_local(n):
    return html.Span(next_update_time(offset=5, output_format="%d.%m.%Y, %H:%M:%S"))


# ------------------------------------------------------------
# -------------------- Stock market clock --------------------
# ------------------------------------------------------------
@app.callback(Output("live-clock-us", "children"), [Input("interval-clock", "n_intervals")])
def live_clock_est(n):
    return html.Span(curr_time(output_format="%H:%M:%S", us_tz=True))


@app.callback(Output("live-next-update-us", "children"), [Input("interval-clock", "n_intervals")])
def live_next_update_us(n):
    return html.Span(next_update_time(offset=5, output_format="%d.%m.%Y, %H:%M:%S", us_tz=True))


# ----------------------------------------------
# -------------------- Plot --------------------
# ----------------------------------------------
@app.callback(Output("live-plot", "figure"), [Input("interval-plot", "n_intervals")])
def live_plot(n):
    """ Function displays live plot. """

    # Loading stock data
    stock_data_path = os.path.join("alphavantage", "tesla_prices.csv")
    assert os.path.isfile(stock_data_path)
    stock_data = pd.read_csv(stock_data_path)

    # Defining the stock candle plot trace
    trace_candle = go.Candlestick(
        x=pd.to_datetime(stock_data.loc[:, "timestamp"]),
        open=stock_data.loc[:, "open"],
        high=stock_data.loc[:, "high"],
        low=stock_data.loc[:, "low"],
        close=stock_data.loc[:, "close"]
    )

    # Plot parameters
    plot_layout = go.Layout(
        title="Stock prices",
        yaxis={"title": "Price (USD)"})

    # Defining plotly figure
    plot_fig = go.Figure(
        data=[trace_candle],
        layout=plot_layout)

    return plot_fig


if __name__ == "__main__":
    app.run_server(debug=True)
