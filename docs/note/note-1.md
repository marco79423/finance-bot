# Note 1

## 目標

完成台股的選股工具包

* 自動搜集股票相關資訊
* 提供選股的工具函式庫（包含回測）
* 完成課程的資優生選股策略

## 發想

* 在 lab/ 建立各種實驗
* 透過 finb serve 啟動服務器
  * 自動更新股票資訊
  * 自動通知 Telegram
  * 提供 API 自動要求更新

## 檔案結構

    conf.d/
        config-template.yml
    docs/
        plans/
            plan-001.md
        notes/
            note-001.md
    finance_bot/
        cmd/  # 參考 paji
            __init__.py
            cli.py
        server/  # 參考 jessigod
        strategy/
            condition/ 
            base.py
        backtest/
        ticker_db/
          model/
          updater/
            yfinance_udpater.py
            finlab_updater.py
            finmind_updater.py
          __init__.py
          ticker_db.py
        tech_tool/
    lab/
        study.ipynb
        test.py
    pyproject.toml 參考 yuki-yaya

## 資料源存儲規則

* 盡量依數據源的格式存儲，先保留下來

## 命令列

```shell
finb serve  # 啟動服務器

finb shell

finb remote update
finb local update
```
