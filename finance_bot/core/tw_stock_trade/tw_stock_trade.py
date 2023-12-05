import uvicorn
import shioaji as sj

from finance_bot.core.base import CoreBase
from finance_bot.infrastructure import infra


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    def __init__(self):
        super().__init__()

        self._shioaji_api = sj.Shioaji()
        self.is_login = False

    def login(self):
        self.logger.info('開始登入永豐證券 ...')
        self._shioaji_api.login(
            api_key=infra.conf.core.tw_stock_trade.shioaji.api_key,
            secret_key=infra.conf.core.tw_stock_trade.shioaji.secret_key,
        )

        ca_path = infra.path.config_folder / 'Sinopac.pfx'
        result = self._shioaji_api.activate_ca(
            ca_path=ca_path,
            ca_passwd=infra.conf.core.tw_stock_trade.shioaji.ca_password,
            person_id=infra.conf.core.tw_stock_trade.shioaji.person_id,
        )
        if not result:
            self.logger.error('永豐憑證啟動失敗')
            return

        self.is_login = True
        self.logger.info('登入永豐證券成功')

    @property
    def account_balance(self):
        if not self.is_login:
            self.login()
        ab = self._shioaji_api.account_balance()
        return ab.acc_balance

    @property
    def positions(self):
        if not self.is_login:
            self.login()
        return [
            dict(
                stock_id=position.code,
                shares=position.quantity * 1000,
                entry_price=position.price,
            )
            for position in self._shioaji_api.list_positions(self._shioaji_api.stock_account)
        ]

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            pass

        uvicorn.run(app, host='0.0.0.0', port=16940)
