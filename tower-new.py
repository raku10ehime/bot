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

    geo_df = gpd.GeoDataFrame(df3, geometry=gpd.points_from_xy(df3.lng, df3.lat), crs=6668)
    ehime = gpd.read_file("N03-20210101_38_GML.zip!N03-20210101_38_GML")

    base = ehime.plot(color="white", edgecolor="black")
    ax = geo_df.plot(ax=base, marker="o", color="red", markersize=5)
    ax.set_axis_off()
    
    plt.savefig("map.png", dpi=200)
    
    consumer_key = os.environ["CONSUMER_KEY"]
    consumer_secret = os.environ["CONSUMER_SECRET"]
    access_token = os.environ["ACCESS_TOKEN"]
    access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
    bearer_token = os.environ["BEARER_TOKEN"]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    
    media_id = api.media_upload("map.png").media_id
    api.update_status(status=twit, media_ids=[media_id])