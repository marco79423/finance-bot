import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from finance_bot.infrastructure import infra
from finance_bot.server.router import debug, tw_stock
from finance_bot.server.service.crypto_loan_service import CryptoLoanService
from finance_bot.server.service.tw_stock_service import TWStockService


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
        def startup():
            # 設定 Service
            if infra.conf.server.service.crypto_loan.enabled:
                service = CryptoLoanService(app)
                service.start()

            if infra.conf.server.service.tw_stock.enabled:
                service = TWStockService(app)
                service.start()
                app.include_router(tw_stock.router)

        uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    server = APIServer()
    server.serve('localhost', 16888, is_dev=True)
