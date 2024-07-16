import random

color_list = [
    "skyblue", 
    "MediumAquamarine", # ミディアム・アクアマリン
    "DarkOliveGreen",
    "HotPink",
    "Indigo",
    "DarkSlateBlue", # ダーク・スレート・ブルー
    "DarkSlateGray", # ダーク・スレート・グレー
    "CornflowerBlue", # コーン・フラワー・ブルー
    "AntiqueWhite",
    "DarkSalmon",
    "LightSalmon",
    "MediumPurple",
    "PaleVioletRed", # ペール・バイオレット・レッド
    "#9e76b4", # アメシスト
    "DarkMagenta" # ダーク・マゼンタ
    ]

# ランダムカラー
def Crandom():
    random_color = color_list[random.randint(0,len(color_list)-1)]
    return random_color