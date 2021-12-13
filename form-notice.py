import datetime
import os
import tweepy

consumer_key = os.environ["CONSUMER_KEY"]
consumer_secret = os.environ["CONSUMER_SECRET"]
access_token = os.environ["ACCESS_TOKEN"]
access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
bearer_token = os.environ["BEARER_TOKEN"]

JST = datetime.timezone(datetime.timedelta(hours=+9))
dt_now = datetime.datetime.now(JST).replace(tzinfo=None)

twit = f"{dt_now:%Y/%m/%d %H:%M}\n\nフォームに投稿がありました\n内容を確認してください"

# print(twit)

client = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)

client.create_tweet(text=twit)
