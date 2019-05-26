import pandas as pd
import requests
import time
from utils import time_until_update

while True:
    try:
        df_old = pd.read_csv("tesla_prices.csv", index_col=0, parse_dates=[0])
    except FileNotFoundError:
        df_old = pd.DataFrame()
    try:
        df = pd.read_csv("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=TSLA&interval=5min&apikey=8YZG2MXVNFPNRIWD&datatype=csv")
        df.set_index("timestamp").iloc[[0]]
    except KeyError:
        continue
    df_old = df_old.append(df)
    df = df.loc[~df.index.duplicated()]
    df.to_csv("tesla_prices.csv")

    # timesleep until 5 minuts, data are in 5 min interval
    wait_time = time_until_update(offset=3).seconds
    for i in range(wait_time):
        print("\rWaiting... %03d" % (wait_time-i), end="")
        time.sleep(1)
