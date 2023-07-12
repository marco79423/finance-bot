# Plan 1

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
        server/  # 參考 jessigod
        lending/
        stock/
          ...
    ...
