import datetime
import os
import time

import geopandas as gpd
import japanize_matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import requests
import tweepy


def get_address(se):

    r = requests.get(
        "https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress",
        params={"lat": se["lat"], "lon": se["lon"]},
    )

    time.sleep(1)

    data = r.json()

    result = data.setdefault("results", {}).get("lv01Nm", "")

    return result


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
df0[["lat", "lon"]] = (
    df0["location"].str.strip("()").str.split(",", expand=True).astype(float)
)

df0["eNB-LCID"] = df0["enb"].astype(str).str.cat(df0["lcid"].astype(str), "-")

df0["date"] = df0["created"].dt.date

df0["場所"] = df0["pref"].str.cat(df0["area1"])

df1 = pd.crosstab(df0["date"], df0["area1"]).reindex(dt_range, fill_value=0)
df1

# 前日
se = df1.iloc[-2]


if se.sum():

    twit = f"MLS 新規登録\n\n{se.name:%Y/%m/%d}\n\n"

    for k, v in se[se > 0].to_dict().items():
        twit += f"{k} : {v}\n"

    twit += f"\n{url}"

    print(twit)

    # 地図

    df2 = df0[df0["date"] == se.name].copy().sort_values(["enb", "lcid"])

    geo_df = gpd.GeoDataFrame(
        df2, geometry=gpd.points_from_xy(df2.lon, df2.lat), crs=6668
    )

    ehime = gpd.read_file("N03-20210101_38_GML.zip!N03-20210101_38_GML")

    base = ehime.plot(color="white", edgecolor="black")
    ax = geo_df.plot(ax=base, marker="o", color="red", markersize=5)
    ax.set_axis_off()

    plt.savefig("map.png", dpi=200)

    # テーブル

    df2["area2"] = df2.apply(get_address, axis=1)
    df2["place"] = df2["area1"].str.cat(df2["area2"])

    df3 = df2["place"].value_counts().rename_axis("place").reset_index(name="counts")

    fig, ax = plt.subplots()

    ax.axis("off")

    ax.table(cellText=df3.values, colLabels=df3.columns, loc="center")
    plt.savefig("table.png", bbox_inches="tight", dpi=300)

    consumer_key = os.environ["CONSUMER_KEY"]
    consumer_secret = os.environ["CONSUMER_SECRET"]
    access_token = os.environ["ACCESS_TOKEN"]
    access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
    bearer_token = os.environ["BEARER_TOKEN"]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    map_id = api.media_upload("map.png").media_id
    table_id = api.media_upload("table.png").media_id

    api.update_status(status=twit, media_ids=[map_id, table_id])
