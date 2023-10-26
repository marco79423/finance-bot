# Note 2

## 目標

完成 lending 機器人

## 發想

* 自動在 bitfinex 借貸
* 每天自動通知狀況
* 提供 API 可以在 telegram 上查詢最新借貸狀況
* 提供 command 可以查詢

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