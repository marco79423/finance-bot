import pandas as pd
import shioaji as sj
from sqlalchemy import select
from sqlalchemy.orm import Session

from finance_bot.core.tw_stock_trade.broker import BrokerBase
from finance_bot.core.tw_stock_trade.broker.base import Position, CommissionInfo
from finance_bot.infrastructure import infra
from finance_bot.model import Wallet


class SinoBroker(BrokerBase):
    name = 'sino_broker'
    commission_info = CommissionInfo(fee_discount=1)

    ca_path = str(infra.path.config_folder / 'Sinopac.pfx')

    def __init__(self):
        super().__init__()

        self._shioaji_api = sj.Shioaji()
        self.is_login = False

    def refresh(self):
        super().refresh()
        self.login()

    def login(self):
        self._shioaji_api = sj.Shioaji()

        self.logger.info('開始登入永豐證券 ...')
        self._shioaji_api.login(
            api_key=infra.conf.core.tw_stock_trade.shioaji.api_key,
            secret_key=infra.conf.core.tw_stock_trade.shioaji.secret_key,
            fetch_contract=False,
        )

        self.logger.info('開始下載商品檔 ...')
        self._shioaji_api.fetch_contracts(
            contract_download=True,
            contracts_timeout=5000,  # 5s
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

    def get_positions(self):
        if not self.is_login:
            self.login()

        result = []
        for position in self._shioaji_api.list_positions(self._shioaji_api.stock_account):
            position_details = self._shioaji_api.list_position_detail(self._shioaji_api.stock_account, position.id)
            if len(position_details) < 1 or len(position_details) > 2:
                raise ValueError('發生不合理的事情')
            result.append(Position(
                stock_id=position.code,
                shares=position.quantity * 1000,
                avg_price=position.price,
                entry_date=pd.Timestamp(position_details[0].date),
            ))
        return result

    def get_current_balance(self):
        with Session(infra.db.engine) as session:
            balance, = session.execute(
                select(Wallet.balance)
                .where(Wallet.code == 'sinopac')
                .limit(1)
            ).first()
        return int(balance)

    def buy_market(self, stock_id, shares, note=''):
        if not self.is_login:
            self.login()

        order = self._shioaji_api.Order(
            price=0,  # 價格
            quantity=shares // 1000,  # 數量
            action=sj.constant.Action.Buy,  # 買賣別
            price_type=sj.constant.StockPriceType.MKT,  # 委託價格類別
            order_type=sj.constant.OrderType.IOC,  # 委託條件
            order_lot=sj.constant.StockOrderLot.Common,  # 整股
            account=self._shioaji_api.stock_account  # 下單帳號
        )

        contract = self._shioaji_api.Contracts.Stocks.TSE[stock_id]
        return self._shioaji_api.place_order(contract, order)

    def sell_market(self, stock_id, shares, note=''):
        if not self.is_login:
            self.login()

        order = self._shioaji_api.Order(
            price=0,  # 價格
            quantity=shares // 1000,  # 數量
            action=sj.constant.Action.Sell,  # 買賣別
            price_type=sj.constant.StockPriceType.MKT,  # 委託價格類別
            order_type=sj.constant.OrderType.IOC,  # 委託條件
            order_lot=sj.constant.StockOrderLot.Common,  # 整股
            account=self._shioaji_api.stock_account  # 下單帳號
        )

        contract = self._shioaji_api.Contracts.Stocks.TSE[stock_id]
        self.logger.info(contract)

        return self._shioaji_api.place_order(contract, order)

    def sell_all_market(self, stock_id, note=''):
        if not self.is_login:
            self.login()

        shares = self.holding_stock_shares_s[stock_id]
        return self.sell_market(stock_id, shares, note)

    def trades(self):
        if not self.is_login:
            self.login()
        return self._shioaji_api.list_trades()

    def update_status(self):
        if not self.is_login:
            self.login()
        self._shioaji_api.update_status(self._shioaji_api.stock_account)

    def cancel_trade(self, trade):
        if not self.is_login:
            self.login()
        self._shioaji_api.cancel_order(trade)

    def get_today_high_price(self, stock_id):
        if not self.is_login:
            self.login()
        contract = self._shioaji_api.Contracts.Stocks.TSE[stock_id]
        return contract.limit_up
