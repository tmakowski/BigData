import pandas as pd
import numpy as np
import datetime as dt
import sys

if __name__ == "__main__":
    df = pd.DataFrame()
    for date in pd.date_range(dt.datetime.strptime(sys.argv[1], "%Y%m%d").date(),
                                dt.datetime.strptime(sys.argv[2], "%Y%m%d").date()):
        df = pd.concat([df, \
            pd.read_json(f"https://api.iextrading.com/1.0/stock/TSLA/chart/date/{date.strftime('%Y%m%d')}")])
    df.loc[df['low']==-1, "low"] = np.NaN
    df['datetime'] = df['date'].astype(str) + df['label']
    df['datetime'] = pd.to_datetime(df['datetime'], format="%Y%m%d%I:%M %p", errors='coerce')
    df = df[['datetime', 'open','high', 'low', 'close', 'marketVolume']]
    df = df.set_index("datetime")
    df = df.resample("5min").agg(["first","last","max", "min", "mean"])[['open', 'high', 'close', 'low', "marketVolume"]]
    df = df[[('open','first'), ('high','max'), ('low','min'), ("close","last"), ("marketVolume","mean")]]
    df = df.dropna()
    df.columns = ['open', 'high', 'low', 'close', 'marketVolume']
    df.to_csv(f"tesla_5m_{sys.argv[1]}_{sys.argv[2]}.csv")
