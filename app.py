# Dash imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Plotly imports
import plotly.graph_objs as go

# Own modules imports
from alphavantage.utils import next_update_time

# Other imports
from datetime import datetime
import pandas as pd
import os


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.H3("🔥 Gouda Praga 🔥"),

    html.Div(id="live-clock"),        # Current time
    html.Div(id="live-next-update"),  # Time when next update will happen
        
    # Plot
    dcc.Graph(id="live-plot"),
        
    # Defining intervals
    dcc.Interval(
        id='interval-clock', n_intervals=0,
        interval=1000*1),  # in milliseconds

    dcc.Interval(
        id='interval-plot', n_intervals=0,
        interval=1000*5)  # in milliseconds
])


STYLE = {"padding": "5px", "fontSize": "16px"}


@app.callback(Output("live-clock", "children"), [Input("interval-clock", "n_intervals")])
def live_clock(n):
    """ Function to display current time. """
    global STYLE
    return html.Span(
        "Current time: %s" % datetime.now().strftime("%H:%M:%S"),
        style=STYLE)


@app.callback(Output("live-next-update", "children"), [Input("interval-clock", "n_intervals")])
def live_next_update(n):
    """ Function displays time when next update will be displayed. """
    global STYLE
    return html.Span(
        "Next update: %s (possible delay: 5 seconds)" % next_update_time(offset=5, format_output=True),
        style=STYLE)


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
