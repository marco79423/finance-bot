import uvicorn
import shioaji as sj

from finance_bot.core.base import CoreBase
from finance_bot.infrastructure import infra


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    def __init__(self):
        api = sj.Shioaji(simulation=True)
        self.accounts = api.login(
            api_key=infra.conf.core.tw_stock_trade.shioaji.api_key,
            secret_key=infra.conf.core.tw_stock_trade.shioaji.secret_key,
        )

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            pass

        uvicorn.run(app, host='0.0.0.0', port=16940)
