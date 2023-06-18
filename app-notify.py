import os
import pandas as pd
import tweepy

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTuN5xiHhlnPTkv3auHkYLT9NPvvjayj5AdPrH5VBQdbELOzfONi236Vub6eSshv8jAxQw3V1rgbbgE/pub?gid=882951423&single=true&output=csv"

df0 = pd.read_csv(
    url,
    parse_dates=["更新日時"],
    dtype={"sector": "Int64", "sub6": "Int64", "ミリ波": "Int64"},
)

# df0

# 投稿回数
df0["count"] = df0.groupby(by="ID").cumcount()

# eNB-LCIDの変更回数
df0["enb_count"] = df0.dropna(subset="eNB-LCID").groupby(by="ID").cumcount()
df0["enb_count"] = df0["enb_count"].fillna(-1).astype(int)

# 欠損を空白文字
df0["eNB-LCID"] = df0["eNB-LCID"].fillna("")
df0["PCI"] = df0["PCI"].fillna("")
df0["基地局ID"] = df0["基地局ID"].fillna("")
df0["URL"] = df0["URL"].fillna("")

# 日付
df0["日付"] = df0["更新日時"].dt.strftime("%Y/%m/%d")

df1 = df0.drop_duplicates(subset=["ID", "場所"], keep="last").copy()

# 現在
dt_now = pd.Timestamp.now(tz="Asia/Tokyo").tz_localize(None)

yesterday = (dt_now - pd.Timedelta(days=1)).date()

df2 = df1[df1["更新日時"].dt.date == yesterday].copy()

def status_check(x):
    result = ""

    if x["count"] > 0:
        if x["enb_count"] > 0:
            result = "eNB-LCID変更"
        else:
            result = "開局"

    else:
        if x["enb_count"] < 0:
            result = "新規発見"
        else:
            result = "新規開局"

    return result

df2["内容"] = df2.apply(status_check, axis=1)
df2["備考"].mask(df2["備考"].isna(), df2["内容"], inplace=True)

df3 = df2[df2["投稿者"] != "@imabarizine"].copy()


# Twitter投稿

consumer_key = os.environ["CONSUMER_KEY"]
consumer_secret = os.environ["CONSUMER_SECRET"]
access_token = os.environ["ACCESS_TOKEN"]
access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
bearer_token = os.environ["BEARER_TOKEN"]

client = tweepy.Client(
    bearer_token, consumer_key, consumer_secret, access_token, access_token_secret
)

for i, row in df3.iterrows():

    latlng = row["地図"].replace(" ", "")

    twit = f'{row["備考"]}\n\n【投稿者】\n{row["投稿者"]}\n\n【日付】\n{row["日付"]}\n\n【場所】\n{row["場所"]}'

    if row["eNB-LCID"]:
        twit += f'\n\n【基地局】\n・eNB-LCID: {row["eNB-LCID"]}\n・PCI: {row["PCI"]}'

        if row["基地局ID"]:
            twit += f'\n・基地局ID: {row["基地局ID"]}'

    twit += f"\n\n【地図】\nhttps://www.google.co.jp/maps?q={latlng}"

    twit += f"\n\n#愛媛 #楽天モバイル #基地局"

    if row["URL"]:
        twit += f'\n\n{row["URL"]}'

    client.create_tweet(text=twit)
