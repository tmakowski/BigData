import tweepy
import json
import datetime

# keys file should contain: consumer_key, consumer_secret, access_token, access_token_secret
with open("keys.json") as keys_file:
    keys = json.load(keys_file)

auth = tweepy.OAuthHandler(keys["consumer_key"], keys["consumer_secret"])
auth.set_access_token(keys["access_token"], keys["access_token_secret"])

class MyStreamListener(tweepy.StreamListener):

    def __init__(self):
        super().__init__()
        self.FILE_NAME = "tweets.json"

    def __enter__(self):
        self.tweets = []
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        with open(self.FILE_NAME, "a") as tweet_file:
            tweet_file.writelines(self.tweets)
        print("Saved data and finished downloading tweets. Date: {}".format(datetime.datetime.now()))

    def on_data(self, data):
        self.tweets.append(data)

if __name__ == "__main__":

    with MyStreamListener() as my_stream_listener:
        print("Started listening to tweets. Date: {}".format(datetime.datetime.now()))
        myStream = tweepy.Stream(auth, my_stream_listener)
        myStream.filter(track=["tesla"], languages=["en"])
