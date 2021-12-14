import datetime
import os

import pandas as pd
import tweepy

url = "https://mls.js2hgw.com/update.php?base_enb=737280"

# 現在の日時
JST = datetime.timezone(datetime.timedelta(hours=+9))
dt_now = datetime.datetime.now(JST).replace(tzinfo=None)

# 日付範囲（８日前から今日まで）
dt_start = (dt_now - datetime.timedelta(days=8)).date()
dt_range = pd.date_range(start=dt_start, end=dt_now.date())

df0 = pd.read_json(
    url + "&output=json", convert_dates=["created", "updated", "modified"]
)

# 空白は不明
df0["area1"].mask(df0["area1"] == "", "不明", inplace=True)

# 経度・緯度
df0[["lat", "lng"]] = (
    df0["location"].str.strip("()").str.split(",", expand=True).astype(float)
)

df0["場所"] = df0["pref"].str.cat(df0["area1"])
df0["eNB-LCID"] = df0["enb"].astype(str).str.cat(df0["lcid"].astype(str), "-")
df0["date"] = df0["created"].dt.date

df1 = pd.crosstab(df0["date"], df0["area1"])

df2 = df1.reindex(dt_range, fill_value=0)

# 前日
se = df2.iloc[-2]

if se.sum():

    twit = f"MLS 新規登録\n\n{se.name:%Y/%m/%d}\n\n"

    for k, v in se[se > 0].to_dict().items():
        twit += f"{k} : {v}\n"

    twit += f"\n{url}"

    print(twit)

    consumer_key = os.environ["CONSUMER_KEY"]
    consumer_secret = os.environ["CONSUMER_SECRET"]
    access_token = os.environ["ACCESS_TOKEN"]
    access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
    bearer_token = os.environ["BEARER_TOKEN"]

    client = tweepy.Client(
        bearer_token, consumer_key, consumer_secret, access_token, access_token_secret
    )
    
    client.create_tweet(text=twit)
