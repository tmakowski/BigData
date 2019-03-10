import tweepy
import json


# keys file should contain: consumer_key, consumer_secret, access_token, access_token_secret
with open("keys.json") as keys_file:
    keys = json.load(keys_file)

auth = tweepy.OAuthHandler(keys["consumer_key"], keys["consumer_secret"])
auth.set_access_token(keys["access_token"], keys["access_token_secret"])

api = tweepy.Stream

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth, myStreamListener)

myStream.filter(track=["tesla"], languages=["en"])
