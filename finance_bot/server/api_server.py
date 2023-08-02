import logging

import fastapi
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from finance_bot.config import conf
from finance_bot.infrastructure import get_now
from finance_bot.server.router import debug, lending, tw_stock
from finance_bot.server.service.lending_service import LendingService
from finance_bot.server.service.tw_stock_service import TWStockService
from utility import get_data_folder


class APIServer:
    def serve(self, host: str, port: int, is_dev: bool):
        # 設定環境
        logging.basicConfig(
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
            format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
        )
        logging.Formatter.converter = lambda *args: get_now().timetuple()
        logging.getLogger('apscheduler').setLevel(logging.WARN)

        # 設定 Scheduler
        logger = logging.getLogger()
        scheduler = AsyncIOScheduler(logger=logger.getChild('scheduler'))

        app = fastapi.FastAPI()
        app.state.logger = logger
        app.state.scheduler = scheduler
        app.state.is_dev = is_dev
        app.state.service = {}

        # 設定第三方擴充
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 設定預設路由
        app.include_router(debug.router)
        app.mount('/data', StaticFiles(directory=get_data_folder()), name="data")

        # 設定 Service
        if conf.server.service.lending:
            service = LendingService(app)
            service.start()
            app.include_router(lending.router)

        if conf.server.service.tw_stock:
            service = TWStockService(app)
            service.start()
            app.include_router(tw_stock.router)

        @app.on_event("startup")
        def startup():
            scheduler.start()

        uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    server = APIServer()
    server.serve('localhost', 8888, is_dev=True)
