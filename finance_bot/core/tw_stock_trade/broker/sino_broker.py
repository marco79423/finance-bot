import pandas as pd
import shioaji as sj

from finance_bot.core.tw_stock_trade.broker import BrokerBase
from finance_bot.core.tw_stock_trade.broker.base import Position, CommissionInfo
from finance_bot.infrastructure import infra


class SinoBroker(BrokerBase):
    name = 'sino_broker'
    commission_info = CommissionInfo(fee_discount=1)

    ca_path = infra.path.config_folder / 'Sinopac.pfx'

    def __init__(self):
        super().__init__()

        self._shioaji_api = sj.Shioaji()
        self.is_login = False

    def refresh(self):
        super().refresh()
        self.login()

    def login(self):
        self.logger.info('開始登入永豐證券 ...')
        self._shioaji_api.login(
            api_key=infra.conf.core.tw_stock_trade.shioaji.api_key,
            secret_key=infra.conf.core.tw_stock_trade.shioaji.secret_key,
        )

        result = self._shioaji_api.activate_ca(
            ca_path=self.ca_path,
            ca_passwd=infra.conf.core.tw_stock_trade.shioaji.ca_password,
            person_id=infra.conf.core.tw_stock_trade.shioaji.person_id,
        )
        if not result:
            self.logger.error('永豐憑證啟動失敗')
            return

        self.is_login = True
        self.logger.info('登入永豐證券成功')

    @property
    def positions(self):
        if not self.is_login:
            self.login()

        result = []
        for position in self._shioaji_api.list_positions(self._shioaji_api.stock_account):
            position_details = self._shioaji_api.list_position_detail(self._shioaji_api.stock_account, position.id)
            if len(position_details) < 1 or len(position_details) > 2:
                raise ValueError('發生不合理的事情')
            result.append(Position(
                id=position.id,
                stock_id=position.code,
                shares=position.quantity * 1000,
                price=position.price,
                date=pd.Timestamp(position_details[0].date),
            ))
        return result

    @property
    def current_balance(self):
        if not self.is_login:
            self.login()
        ab = self._shioaji_api.account_balance()
        return ab.acc_balance

    def buy_market(self, stock_id, shares, note=''):
        """發現沒錢就自動放棄購買"""
        pass

    def sell_all_market(self, stock_id, note=''):
        pass
