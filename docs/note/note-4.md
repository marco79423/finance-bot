# Note 4

## 目標

* 建立容易操作、畫圖表、分析的方式
* 自動抓個股綜合財報
* 自動抓每月營收財報
* 靜態資料夾呈現下載的財報

## 檔案結構

    finance_bot/
        cmd/  # 參考 paji
            __init__.py
            cli.py
        shell/
        server/
            service/
                lending.py
        core/
            lending/
            tw_stock/
        model/
        infrastructure/
          ...
    ...

## 設定檔

```yaml
server:
  
  service:
    lending:
      enabled: true
      schedule:
        lending_task: '*/10 * * * *'
        sending_stats:
          - '0 8 * * mon,tue,wed,thu,fri'
          - '0 12 * * sat,sun'
    tw_stock: 
      enabled: true
      schedule:
        schedule_update_task:
          - '0 8 * * mon,tue,wed,thu,fri'
          - '0 12 * * sat'
core:
  lending:
    api_key: <key>
    api_secret: <token>
    schedule:
      lending_task: '*/10 * * * *'
      sending_stats:
        - '0 8 * * mon,tue,wed,thu,fri'
        - '0 12 * * sat,sun'
  
  tw_stock:
    
    schedule:
      schedule_update_task:
        - '0 8 * * mon,tue,wed,thu,fri'
        - '0 12 * * sat'
    updater:
      finmind:
        api_token: <token>
      finlab:
        api_token: <token>
infrastructure:
  timezone: Asia/Taipei
  database:
    url: <url>
    async_url: <url>
  notification:
    telegram:
      chat_id: <chat_id>
      token: <token>
```
