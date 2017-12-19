# ミッキーフェイス判定機 for slack

Python2系で実施。
下記をpip installしたライブラリ群(site-package.zip)をAzure Functionsのwwwroot直下に配置すること
- BeautifulSoup4
- requests

Azure FunctionsはPythonのHTTPトリガー(GET)を利用

### これから追加しないといけない機能
- slack キックワードの設定
- 画像サイズが大きすぎる場合のリサイズ処理
- minetypeを使ったバリデーションチェック
- ミニー判定