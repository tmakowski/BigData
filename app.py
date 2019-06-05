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
import json

# models imports
from xgboost import XGBRegressor
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import Lasso

# Explainers import
import matplotlib.pyplot as plt
import matplotlib
import shap
from io import BytesIO
import base64
import glob
import os


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
        [html.Tr([html.Th(col) for col in dataframe.columns])] +
        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ], style={'background': "#982000"}) if dataframe.iloc[i]['preds'] < 0 else
         html.Tr([
             html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
         ], style={'background': "#90EE90"})
         for i in range(min(len(dataframe), max_rows))]
    )


def format_tweet(df, positive_flag):
    if positive_flag:
        main_color = "#1E88E5"
    else:
        main_color = "#FF0D57"

    div_list = []
    for body_text, pred in zip(df["text"], df["preds"]):
        # Tweet body
        div_list.append(html.Blockquote(html.P(body_text), className="twitter-tweet",
                                        style={"border-color": main_color, "text-align": "left"}))
        # Pred
        div_list.append(html.Div("%.3f" % pred,
                                 style={"color": main_color, "text-align": "right",
                                        "margin-bottom": "0.3em", "margin-right": "0.75em"}, className="score"))

    return html.Div(div_list)


TEXT_COLOR = "#ffffff"
BACKGROUND_COLOR = "#37474f"
UPDATE_OFFSET = 5
SIDE_PANELS_STYLE = {
    "display": "inline-block",
    "width": "16vw",
    "fontSize": "16px",
    "padding": "5px",
    "text-align": "center",
    "vertical-align": "top"}

CENTER_PANEL_WIDTH = "66vw"
CENTER_PANEL_STYLE = {
    "width": CENTER_PANEL_WIDTH,
    "display": "inline-block",
    "text-align": "center",
    "padding-left": "5px",
    "padding-right": "5px"}

PAGE_STYLE = {
    "background-color": "#37474f", "width": "100%", "height": "100%", 'margin': 0}
BORDER_STYLE = {"border-style": "solid", "border-width": "1px", "border-color": "white"}

# Loading models
xgb = joblib.load("models/xgboost_price.h5")
cv = joblib.load("models/count_vectorizer.h5")
lasso = joblib.load("models/tweets_model.h5")

app = dash.Dash(__name__, assets_folder="app_files/app_css")
app.layout = html.Div([
    # Technical elements
    html.Div([
        html.Div(id="data-div"), html.Div(id="explainer"), html.Pre(id="selected-data"),
        html.Div(id="tweets-div")], style={"display": "none"}),

    # Defining intervals (in milliseconds)
    dcc.Interval(id='interval-clock', n_intervals=0, interval=1000 * 1),
    dcc.Interval(id='interval-plot', n_intervals=0, interval=1000 * 5),
    dcc.Interval(id='interval-alpha', n_intervals=0, interval=1000 * 300),

    # Local time clock
    html.Div([
        html.Div([
            html.Div("Local time"), html.Div(id="live-clock-local"),
            html.Div("Next update at"), html.Div(id="live-next-update-local", className="update")
        ], style={**SIDE_PANELS_STYLE, **BORDER_STYLE}),

        # Gouda Praga
        html.Div(id="model-output", style=CENTER_PANEL_STYLE),

        # Stock market time clock
        html.Div([
            html.Div("Stock market time"), html.Div(id="live-clock-us"),
            html.Div("Next update at"), html.Div(id="live-next-update-us", className="update")
        ], style={**SIDE_PANELS_STYLE, **BORDER_STYLE})]),

    # Body with plot
    html.Div([
        # Left panel
        html.Div([
            html.H4("Latest negative scores", style={"color": "#FF0D57"}),
            html.Div(id="tweets-negative")
        ], style=SIDE_PANELS_STYLE),

        html.Div([
            # dcc.Dropdown(id="plot-mode-dropdown", value=1, style={"color": "black", "margin-top": "0.5em", "margin-bottom": "0.5em"},
            #              options=[
            #                  {"label": "Last 24h", "value": 1},
            #                  {"label": "Historic data", "value": 0}]),
            dcc.Graph(id="live-plot", style={"margin-top": "0.5em"}),  # Candlestick plot
            html.Div(id="explain-desc"),
            html.Img(id='explain-plot', src='', style={"width": CENTER_PANEL_WIDTH, "text-align": "center"})
            # Explainer
        ], style=CENTER_PANEL_STYLE),

        # Right panel
        html.Div([
            html.H4("Latest positive scores", style={"color": "#1E88E5"}),
            html.Div(id="tweets-positive")
        ], style=SIDE_PANELS_STYLE)
    ], style={"display": "inline-block"}),

])


# TWEETS taking and predicting
@app.callback(Output("tweets-div", "children"), [Input("interval-clock", "n_intervals")])
def update_tweets(n):
    list_of_files = glob.glob('/user/spark/test_online_evaluation/*.csv') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    tweets = pd.read_csv(latest_file, sep=",", header=None, names=["id","text","preds"])
    tweets = tweets.dropna()

    # list_of_files = glob.glob('data/*_example.csv')
    # latest_file = max(list_of_files, key=os.path.getctime)
    # tweets = pd.read_csv(latest_file, index_col=0, parse_dates=[0])
    # tweets["preds"] = lasso.predict(cv.transform(tweets['text']))
    # tweets = tweets.reset_index()
    return tweets.to_json()


@app.callback(Output("tweets-negative", "children"), [Input("tweets-div", "children")])
def tweets_negative(df):
    tweets = pd.read_json(df)
    top5_negative = tweets[tweets.preds < 0].iloc[:5, :]

    return format_tweet(top5_negative, positive_flag=False)


@app.callback(Output("tweets-positive", "children"), [Input("tweets-div", "children")])
def tweets_positive(df):
    tweets = pd.read_json(df)
    top5_positive = tweets[tweets.preds > 0].iloc[:5, :]

    return format_tweet(top5_positive, positive_flag=True)


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
@app.callback(Output("live-plot", "figure"), [Input("interval-plot", "n_intervals")])
def live_plot(n):
    """ Function displays live plot. """

    # Loading stock data

    stock_data = pd.read_csv(
        "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=TSLA&interval=5min&apikey=8YZG2MXVNFPNRIWD&datatype=csv")

    # Last 24h
    stock_data["timestamp"] = pd.to_datetime(stock_data.loc[:, "timestamp"])
    stock_data = stock_data[stock_data.timestamp >= curr_time(us_tz=True).replace(tzinfo=None) - timedelta(hours=24)]

    # Defining the stock candle plot trace
    trace_candle = go.Candlestick(
        x=pd.to_datetime(stock_data.loc[:, "timestamp"]),
        open=stock_data.loc[:, "open"],
        high=stock_data.loc[:, "high"],
        low=stock_data.loc[:, "low"],
        close=stock_data.loc[:, "close"])

    # Plot parameters
    plot_layout = go.Layout(
        title="<b>Stock prices</b>",
        yaxis={"title": "Price (USD)"},
        clickmode="event+select",
        uirevision=False)

    # Defining plotly figure
    plot_fig = go.Figure(
        data=[trace_candle],
        layout=plot_layout)

    return plot_fig


@app.callback(Output("data-div", "children"), [Input("interval-plot", "n_intervals")])
def model_predict(n):
    df = pd.read_csv(
        "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=TSLA&interval=5min&apikey=8YZG2MXVNFPNRIWD&datatype=csv")
    df = df.set_index("timestamp").sort_index()
    df = add_all_ta_features(df, "open", 'high', 'low', 'close', 'volume')
    df['lower_shadow'] = np.minimum(df['open'], df['close']) - df['low']
    df['higher_shadow'] = df['high'] - np.maximum(df['open'], df['close'])
    df['profit'] = (df['close'] - df['open']).shift(-1)
    X = df.drop(['profit', 'others_dlr', 'others_dr', 'others_cr'], axis=1)
    df['preds'] = xgb.predict(X[xgb.get_booster().feature_names])
    df['profit_model'] = np.where(df['preds'] > 0, df['profit'], -df['profit'])
    return df.to_json()


@app.callback([Output(component_id='explain-plot', component_property='src'), Output("explain-desc", "children")],
              [Input("data-div", "children"), Input("selected-data", "children")])
def explain_model(df, selected):
    df = pd.read_json(df)
    if selected != "null":
        selected = json.loads(selected)['points'][0]
        idx = selected['x']
    else:
        idx = df.index.values[-1]
    X = df[xgb.get_booster().feature_names].round(2).loc[idx]
    explainer = shap.TreeExplainer(xgb)
    shap_values = explainer.shap_values(X)
    # matplotlib.rcParams.update(matplotlib.rcParamsDefault)
    matplotlib.rcParams.update({
        # Axis coloring
        "xtick.color": TEXT_COLOR, "axes.edgecolor": TEXT_COLOR,

        # Axis size
        "xtick.major.size": 10, "xtick.labelsize": 15,

        'text.color': "black",
        # "axes.labelcolor": TEXT_COLOR,
        "axes.facecolor": BACKGROUND_COLOR
    })
    fig = shap.force_plot(explainer.expected_value, shap_values, X.round(2), matplotlib=True, show=False)
    fig.tight_layout()
    out_url = fig_to_url(fig, facecolor=BACKGROUND_COLOR)

    explain_date = idx if isinstance(idx, str) else pd.to_datetime(idx).strftime("%Y-%m-%d %H:%M")
    return out_url, html.H4("Model breakdown for %s" % explain_date,
                            style={
                                "color": "#1E88E5" if df.loc[idx]["preds"] > 0 else "#FF0D57",
                                "padding": 5, "font-weight": "bold"})


# ------------------------------------------------------
# -------------------- Model output --------------------
# ------------------------------------------------------

@app.callback(Output("model-output", "children"), [Input("data-div", "children")])
def model_output_display(df):
    df = pd.read_json(df)
    return html.Div([html.Br(), html.H3("🔥 Gouda Praga 🔥"), html.Br()],
                    style={"background-color": "green" if df.iloc[-1]["preds"] > 0 else "red"})


@app.callback(Output("selected-data", "children"), [Input("live-plot", "selectedData")])
def model_output_display(k):
    return json.dumps(k, indent=2)


if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=8049)