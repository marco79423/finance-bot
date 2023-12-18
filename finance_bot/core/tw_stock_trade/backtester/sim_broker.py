from finance_bot.core.tw_stock_trade.broker.base import BrokerBase, Position, CommissionInfo


class SimBroker(BrokerBase):
    name = 'sim_broker'
    commission_info = CommissionInfo(fee_discount=0.6)

    def __init__(self, data, init_balance):
        super().__init__()
        self._data = data
        self._init_balance = init_balance
        self._balance = init_balance

        self._current_idx = 0
        self._positions = []
        self._positions_cache = {}
        self._trade_logs = []

    def buy_market(self, stock_id, shares, note=''):
        entry_price = self._data.get_stock_open_price(stock_id)

        before = self.current_balance
        fee = self.commission_info.get_buy_commission(entry_price, shares)
        funds = int(shares * entry_price) + fee
        after = before - funds

        # 發現為負值就放棄購買
        if after < 0:
            return

        # 先寫 log
        self._trade_logs.append({
            'idx': self._current_idx,
            'date': self._data.current_time,
            'action': 'buy',
            'stock_id': stock_id,
            'shares': shares,
            'fee': fee,
            'price': entry_price,
            'before': before,
            'funds': -funds,
            'after': after,
            'note': note,
        })

        # 執行交易
        if stock_id not in self._positions_cache:
            self._positions_cache[stock_id] = {}

        self._positions.append(Position(
            id=self._current_idx,
            stock_id=stock_id,
            shares=shares,
            date=self._data.current_time,
            price=entry_price
        ))

        self._positions_cache[stock_id][self._current_idx] = {
            'idx': self._current_idx,
            'stock_id': stock_id,
            'shares': shares,
            'start_date': self._data.current_time,
            'start_price': entry_price,
        }
        self._balance = after
        self._current_idx += 1

        return True

    def sell_all_market(self, stock_id, note=''):
        if stock_id not in self._positions_cache:
            return False

        price = self._data.get_stock_open_price(stock_id)

        for position in self._positions_cache[stock_id].values():
            before = self.current_balance
            fee = self.commission_info.get_sell_commission(price, position['shares'])
            funds = int(position['shares'] * price) - fee
            after = before + funds

            # 先寫 log
            self._trade_logs.append({
                'idx': position['idx'],
                'date': self._data.current_time,
                'action': 'sell',
                'stock_id': stock_id,
                'shares': position['shares'],
                'fee': fee,
                'price': price,
                'before': before,
                'funds': funds,
                'after': after,
                'note': note,
            })

            # 執行交易
            self._balance = after

        self._positions = [position for position in self._positions if position.stock_id != stock_id]
        del self._positions_cache[stock_id]

        return True

    @property
    def current_balance(self):
        return self._balance

    @property
    def positions(self):
        return self._positions

    @property
    def init_balance(self):
        return self._init_balance

    @property
    def trade_logs(self):
        return self._trade_logs
