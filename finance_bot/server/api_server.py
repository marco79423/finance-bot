import logging
import fastapi
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi.middleware.cors import CORSMiddleware

from finance_bot.server.router import debug


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
        scheduler.start()

        app = fastapi.FastAPI()
        app.state.logger = logging.getLogger()
        app.state.scheduler = scheduler
        app.state.is_dev = is_dev

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

        uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    server = APIServer()
    server.serve('localhost', 8888, is_dev=True)
