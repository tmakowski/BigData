import pandas as pd
import requests
import time

while True:
    try:
        df_old = pd.read_csv("tesla_prices.csv", index_col=0, parse_dates=[0])
    except FileNotFoundError:
        df_old = pd.DataFrame()
    df = pd.read_csv("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=TSLA&interval=5min&apikey=8YZG2MXVNFPNRIWD&datatype=csv")
    df.set_index("timestamp").iloc[[0]]
    df_old = df_old.append(df)
    df = df.loc[~df.index.duplicated()]
    df.to_csv("tesla_prices.csv")
    time.sleep(5) #timesleep 5 minuts, data are in 5 min interval
