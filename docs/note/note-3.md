# Note 3

## 目標

真．爬蟲

## 發想

* 定時運作的爬蟲
* 去爬公開資訊站的股價
* 調整 DB 結構
* 調整效能
* 限制範圍

## 限制

* TWSE 的個股
* ETF

## 檔案結構

    finance_bot/
        cmd/  # 參考 paji
            __init__.py
            cli.py
        server/
            daemon/
                lending.py
        lending/
        tw_stock/
        infrastructure/
          ...
    ...

## 設定檔

```yaml
general:
  timezone: Asia/Taipei

lending:
  enabled: false
  api_key: <token>
  api_secret: <token>
  schdule:
    lending_task: '* * * * *'
    sending_stats: '0 8 * * *'

tw_stock:
  database:
    url: <url>
  updater:
    findmind:
      api_token: <token>
    finlab:
      api_token: <token>

notification:
  telegram:
    chat_id: <url>
    token: <token>

```

## API 定義

    /lending/stats
    /lending/wallets