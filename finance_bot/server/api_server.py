import logging
import fastapi
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.middleware.cors import CORSMiddleware

from finance_bot.config import conf
from finance_bot.server.daemon.lending_daemon import LendingDaemon
from finance_bot.server.daemon.tw_stock_daemon import TWStockDaemon
from finance_bot.server.router import debug, lending, tw_stock


class APIServer:
    def serve(self, host: str, port: int, is_dev: bool):
        # 設定環境
        logging.basicConfig(
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
            format='[%(asctime)s][%(levelname)s] %(message)s',
        )

        # 設定 Scheduler
        scheduler = AsyncIOScheduler()

        app = fastapi.FastAPI()
        app.state.logger = logging.getLogger()
        app.state.scheduler = scheduler
        app.state.is_dev = is_dev
        app.state.daemon = {}

        # 設定第三方擴充
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 設定路由
        app.include_router(debug.router)

        # 設定 Daemon
        if conf.server.daemon.lending:
            app.state.logger.info('啟動 Lending 功能')
            daemon = LendingDaemon(app)
            daemon.start()
            app.state.daemon['lending'] = daemon
            app.include_router(lending.router)

        if conf.server.daemon.tw_stock:
            app.state.logger.info('啟動 TW Stock 功能')
            daemon = TWStockDaemon(app)
            daemon.start()
            app.state.daemon['tw_stock'] = daemon
            app.include_router(tw_stock.router)

        @app.on_event("startup")
        def startup():
            scheduler.start()

        uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    server = APIServer()
    server.serve('localhost', 8888, is_dev=True)
