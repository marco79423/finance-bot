import uvicorn
import shioaji as sj

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_trade.broker import SinoBroker


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    def __init__(self):
        super().__init__()

        self._broker = SinoBroker()

    @property
    def account_balance(self):
        return self._broker.current_balance

    @property
    def current_holding(self):
        return self._broker.current_holding

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            pass

        uvicorn.run(app, host='0.0.0.0', port=16940)
