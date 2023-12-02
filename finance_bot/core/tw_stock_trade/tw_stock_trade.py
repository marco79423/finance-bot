import uvicorn

from finance_bot.core.base import CoreBase


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            pass

        uvicorn.run(app, host='0.0.0.0', port=16940)
