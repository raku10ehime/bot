import os
import pandas as pd
import tweepy

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRDgDbpuBUvGcK7TJKiwMSIfs5yi95qmERjZ_iXHMWSRDlarjwUoDVdvpXOB8a2zpnwpq4Vj9VBHJcf/pub?gid=1103909932&single=true&output=csv"

df0 = pd.read_csv(url, usecols=[2, 3, 4, 5], index_col="市区町村名")

df0.index = df0.index.str.replace("^(越智郡|上浮穴郡|伊予郡|喜多郡|西宇和郡|北宇和郡|南宇和郡)", "", regex=True)

# 更新チェック
df1 = df0[df0["前日比"] != 0]

if len(df1) > 0:

    consumer_key = os.environ["CONSUMER_KEY"]
    consumer_secret = os.environ["CONSUMER_SECRET"]
    access_token = os.environ["ACCESS_TOKEN"]
    access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
    bearer_token = os.environ["BEARER_TOKEN"]

    cities = []

    for i, row in df1.iterrows():
        cities.append(f"{row.name} {row.iloc[2]:+}")

    text = "\n".join(cities)

    twit = f"{df1.columns[0]}\n\n楽天モバイル エリア更新\n\n{text}\n\nhttps://docs.google.com/spreadsheets/d/e/2PACX-1vRDgDbpuBUvGcK7TJKiwMSIfs5yi95qmERjZ_iXHMWSRDlarjwUoDVdvpXOB8a2zpnwpq4Vj9VBHJcf/pubhtml\n\n#楽天モバイル #愛媛 #基地局"

    print(twit)

    client = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)
    client.create_tweet(text=twit)
