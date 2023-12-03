import uvicorn

from finance_bot.core.base import CoreBase


class SuperBot(CoreBase):
    name = 'super_bot'

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            pass

        uvicorn.run(app, host='0.0.0.0', port=16950)
