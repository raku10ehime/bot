import os
import re
import urllib.parse

import pandas as pd
import plotly.figure_factory as ff
import requests
import tweepy

d = {
    # 1:免許情報検索  2: 登録情報検索
    "ST": 1,
    # 詳細情報付加 0:なし 1:あり
    "DA": 1,
    # スタートカウント
    "SC": 1,
    # 取得件数
    "DC": 1,
    # 出力形式 1:CSV 2:JSON 3:XML
    "OF": 2,
    # 無線局の種別
    "OW": "FB_H",
    # 所轄総合通信局
    "IT": "G",
    # 免許人名称/登録人名称
    "NA": "楽天モバイル",
}

parm = urllib.parse.urlencode(d, encoding="shift-jis")

r = requests.get("https://www.tele.soumu.go.jp/musen/list", parm)
data = r.json()

update = data["musenInformation"]["lastUpdateDate"]

s = (
    data["musen"][0]["detailInfo"]["note"]
    .split("\\n", 2)[2]
    .replace("\\n", " ")
    .strip()
)

lst = re.findall("(\S+)\(([0-9,]+)\)", s)

df0 = pd.DataFrame(lst, columns=["市区町村名", "開設局数"])

df0["開設局数"] = df0["開設局数"].str.strip().str.replace(",", "").astype(int)

flag = df0["市区町村名"].str.endswith(("都", "道", "府", "県"))

df0["都道府県名"] = df0["市区町村名"].where(flag).fillna(method="ffill")

df1 = df0[(df0["都道府県名"] == "愛媛県") & (df0["市区町村名"] != "愛媛県")].copy()

df2 = df1.sort_values(by="開設局数", ascending=False).reset_index(drop=True)

df2["順位"] = (
    df2["開設局数"].rank(ascending=False, method="min", numeric_only=True).astype(int)
)

df3 = (
    df2.reindex(columns=["順位", "市区町村名", "開設局数"])
    .rename(columns={"開設局数": update})
    .set_index("順位")
)

df3

# Image

fig = ff.create_table(df3)

fig.write_image("ehime.png", engine="kaleido", scale=10)

# Twitter

consumer_key = os.environ["CONSUMER_KEY"]
consumer_secret = os.environ["CONSUMER_SECRET"]
access_token = os.environ["ACCESS_TOKEN"]
access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
bearer_token = os.environ["BEARER_TOKEN"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

image_id = api.media_upload("ehime.png").media_id

twit = f'{update}現在 市町村別包括免許'

api.update_status(status=twit, media_ids=[image_id])
