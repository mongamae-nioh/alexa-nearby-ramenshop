# 位置情報の共有を許可するように促すカードをAlexaアプリへ表示する関数の引数
permissions = ["alexa::devices:all:geolocation:read"]

# Alexaアプリのカードや画面付きデバイスへ表示するタイトル
card_title = "紹介したお店と現在地からの距離"

# 探したいメニュー
search_menu = 'ラーメン'

# 検索範囲 緯度/経度からの検索範囲(半径) 1:300m、2:500m、3:1000m、4:2000m、5:3000m
search_range = 4

# 一度の発話で紹介する口コミの数
referrals_at_once = 2
