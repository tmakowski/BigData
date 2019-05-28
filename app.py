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
from datetime import timedelta
import pandas as pd
import numpy as np
import os
from ta import add_all_ta_features

#models imports
from xgboost import XGBRegressor
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import Lasso

#Explainers import
import matplotlib.pyplot as plt
import shap
from io import BytesIO
import base64


def fig_to_url(in_fig, close_all=True, **save_args):
    # type: (plt.Figure) -> str
    """
    Save a figure as a URI
    :param in_fig:
    :return:
    """
    out_img = BytesIO()
    in_fig.savefig(out_img, format='png', **save_args)
    if close_all:
        in_fig.clf()
        plt.close('all')
    out_img.seek(0)  # rewind file
    encoded = base64.b64encode(out_img.read()).decode("ascii").replace("\n", "")
    return "data:image/png;base64,{}".format(encoded)

def generate_table(dataframe, max_rows=26):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns]) ] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


UPDATE_OFFSET = 5
CLOCK_STYLE = {
    "display": "inline-block",
    "width": "14%",
    "fontSize": "16px",
    "padding": "5px",
    "textAlign": "center"
}

#Loading models
xgb = joblib.load("models/xgboost_price.h5")
cv = joblib.load("models/count_vectorizer.h5")
lasso = joblib.load("models/tweets_model.h5")
tweets = pd.read_csv("data/tweets_example.csv", index_col=0, parse_dates=[0])
preds = lasso.predict(cv.transform(tweets['text']))
tweets['preds'] = preds

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    # Defining intervals (in milliseconds)
    dcc.Interval(id='interval-clock', n_intervals=0, interval=1000*1),
    dcc.Interval(id='interval-plot', n_intervals=0, interval=1000*5),

    # Local time clock
    html.Div([
        html.Div("Local time"), html.Div(id="live-clock-local"),
        html.Div("Next update at"), html.Div(id="live-next-update-local")
    ], style=CLOCK_STYLE),

    # Gouda Praga
    html.Div([
        html.H3(id="model-output"),
    ], style={"width": "69%", "display": "inline-block", "textAlign": "center"}),

    # Stock market time clock
    html.Div([
        html.Div("Stock market time"), html.Div(id="live-clock-us"),
        html.Div("Next update at"), html.Div(id="live-next-update-us")
    ], style=CLOCK_STYLE),
    html.Div(id="data-div", style={"display":"none"}),
    html.Div(id="explainer", style={"display":"none"}),

    # Choose mode
    dcc.Dropdown(id="plot-mode-dropdown", options=[
        {"label": "Last 24h", "value": 1},
        {"label": "Historic data", "value": 0}
    ], value=1),
    # Candlestick plot
    dcc.Graph(id="live-plot"),

    # Profit plot
    #dcc.Graph(id='profit-plot'),
    html.Div([html.Img(id = 'explain-plot', src = '')],
             id='plot_div'),
    generate_table(tweets)
    # Defining intervals (in milliseconds)




])


# -----------------------------------------------------
# -------------------- Local clock --------------------
# -----------------------------------------------------
@app.callback(Output("live-clock-local", "children"), [Input("interval-clock", "n_intervals")])
def live_clock_local(n):
    return html.Span(curr_time(output_format="%H:%M:%S"))


@app.callback(Output("live-next-update-local", "children"), [Input("interval-clock", "n_intervals")])
def live_next_update_local(n):
    return html.Span(next_update_time(offset=UPDATE_OFFSET, output_format="%d.%m.%Y, %H:%M:%S"))


# ------------------------------------------------------------
# -------------------- Stock market clock --------------------
# ------------------------------------------------------------
@app.callback(Output("live-clock-us", "children"), [Input("interval-clock", "n_intervals")])
def live_clock_est(n):
    return html.Span(curr_time(output_format="%H:%M:%S", us_tz=True))


@app.callback(Output("live-next-update-us", "children"), [Input("interval-clock", "n_intervals")])
def live_next_update_us(n):
    return html.Span(next_update_time(offset=UPDATE_OFFSET, output_format="%d.%m.%Y, %H:%M:%S", us_tz=True))


# ----------------------------------------------
# -------------------- Plot --------------------
# ----------------------------------------------
@app.callback(Output("live-plot", "figure"), [Input("interval-plot", "n_intervals"), Input("plot-mode-dropdown", "value")])
def live_plot(n, mode):
    """ Function displays live plot. """

    # Loading stock data
    stock_data_path = os.path.join("alphavantage", "tesla_prices.csv")
    assert os.path.isfile(stock_data_path)
    stock_data = pd.read_csv(stock_data_path)

    # Last 24h
    if mode:
        stock_data["timestamp"] = pd.to_datetime(stock_data.loc[:, "timestamp"])
        stock_data = stock_data[stock_data.timestamp >= curr_time(us_tz=True).replace(tzinfo=None) - timedelta(hours=24)]

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
        yaxis={"title": "Price (USD)"},
        uirevision=mode)

    # Defining plotly figure
    plot_fig = go.Figure(
        data=[trace_candle],
        layout=plot_layout)

    return plot_fig



@app.callback(Output("data-div", "children"), [Input("interval-plot", "n_intervals")])
def model_predict(n):
    stock_data_path = os.path.join("alphavantage", "tesla_prices.csv")
    assert os.path.isfile(stock_data_path)
    stock_data = pd.read_csv(stock_data_path, index_col=0)
    stock_data = stock_data.set_index("timestamp").sort_index()
    df = add_all_ta_features(stock_data, "open", 'high','low', 'close', 'volume')
    df['lower_shadow'] = np.minimum(df['open'], df['close']) - df['low']
    df['higher_shadow'] = df['high'] - np.maximum(df['open'], df['close'])
    df['profit'] = (df['close'] - df['open']).shift(-1)
    X = df.drop(['profit', 'others_dlr','others_dr', 'others_cr'],axis=1)
    df['preds'] = xgb.predict(X[xgb.get_booster().feature_names])
    df['profit_model'] = np.where(df['preds'] > 0, df['profit'], -df['profit'])
    return df.to_json()

@app.callback(Output(component_id='explain-plot', component_property='src'), [Input("data-div","children")])
def explain_model(df):
    df = pd.read_json(df)
    X = df[xgb.get_booster().feature_names].round(2)
    explainer = shap.TreeExplainer(xgb)
    shap_values = explainer.shap_values(X)
    fig = shap.force_plot(explainer.expected_value, shap_values[-1,:], X.iloc[-1,:].round(2), matplotlib=True, show=False)
    out_url = fig_to_url(fig)
    return out_url



# ------------------------------------------------------
# -------------------- Model output --------------------
# ------------------------------------------------------
@app.callback(Output("model-output", "children"), [Input("interval-plot", "n_intervals"), Input("plot-mode-dropdown", "value")])
def model_output_display(n, model_prediction):
    return html.H3("🔥 Gouda Praga 🔥",
                   style={"background-color": "green" if model_prediction else "red"})


if __name__ == "__main__":
    app.run_server(debug=True)
