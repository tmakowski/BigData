import numpy as np
import pandas as pd
import tweepy
import datetime
import json
import re
import argparse

from credentials import *

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

class MyStreamListener(tweepy.StreamListener):

    def __init__(self, name):
        super().__init__()
        self.FILE_NAME = str(name) + '.csv'

    def __enter__(self):
        self.tweets = []
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        print("Saved data and finished downloading tweets. Date: {}".format(datetime.datetime.now()))
        if (exception_type == KeyboardInterrupt):
            print("Exiting program because of KeyboardInterrupt")
            return True

    def on_data(self, data):
        # string to dict
        data = json.loads(data)
        # print(data.get('text'))
        # if no id or if it's retweet do nothing
        if data.get('id') and re.search('^RT', data.get('text')) == None: 
            data = pd.DataFrame(data=[[data.get('id'), data.get('text'), data.get('created_at'), data.get('favorite_count'), data.get('retweet_count')]], columns=['id','text','created_at','favorive_count','retweet_count'])
            # remove \n from text
            data['text'] = data['text'].replace(to_replace= '\\n', value= '', regex=True)
            with open(self.FILE_NAME, 'a', encoding="utf-8") as f:
                data.to_csv(f, header=False, index = False, line_terminator = '\n', sep = ',')

if __name__ == "__main__":
    # argparse Pozwala wywołać program z argumentami z poziomu konsoli np. twitter_api.py tesla
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    args = parser.parse_args()
    # args.query - wartość wczytana z konsoli

    # Strumień
    with MyStreamListener(args.query) as my_stream_listener:
        print("Started listening to tweets. Date: {}".format(datetime.datetime.now()))
        myStream = tweepy.Stream(auth, my_stream_listener)
        myStream.filter(track=[str(args.query)], languages=["en"])

