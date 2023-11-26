import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from finance_bot.infrastructure import infra
from finance_bot.server.router import debug
from finance_bot.server.service.crypto_loan_service import CryptoLoanService
from finance_bot.server.service.data_sync_service import DataSyncService
from finance_bot.server.service.schedule_service import ScheduleService


class APIServer:
    def serve(self, host: str, port: int, is_dev: bool):
        app = fastapi.FastAPI()
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
        app.mount('/data', StaticFiles(directory=infra.path.data_folder), name="data")

        @app.on_event("startup")
        async def startup():
            # 設定 Service
            if infra.conf.server.service.crypto_loan.enabled:
                service = CryptoLoanService(app)
                await service.start()

            if infra.conf.server.service.data_sync.enabled:
                service = DataSyncService(app)
                await service.start()

            service = ScheduleService(app)
            await service.start()

        uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    server = APIServer()
    server.serve('localhost', 16888, is_dev=True)
