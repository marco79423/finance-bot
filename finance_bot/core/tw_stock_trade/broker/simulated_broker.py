from finance_bot.core.tw_stock_trade.broker.base import BrokerBase, Position, CommissionInfo


class SimulatedBroker(BrokerBase):
    name = 'simulated_broker'
    commission_info = CommissionInfo(fee_discount=1)

    def __init__(self, data, init_balance):
        super().__init__()
        self._data = data
        self._init_balance = init_balance
        self._balance = init_balance

        self._current_index = 0
        self._position_map = {}
        self._positions_cache = {}
        self._trade_logs = []

    def buy_market(self, stock_id, shares, note=''):
        entry_price = self._data.get_stock_open_price(stock_id)

        before = self.current_balance
        fee = self.commission_info.get_buy_commission(entry_price * shares)
        amount = int(shares * entry_price) + fee
        after = before - amount

        # 發現為負值就放棄購買
        if after < 0:
            return

        # 先寫 log
        self._trade_logs.append({
            'index': self._current_index,
            'date': self._data.current_time.isoformat(),
            'action': 'buy',
            'stock_id': stock_id,
            'shares': shares,
            'fee': fee,
            'price': entry_price,
            'amount': -amount,
            'note': note,
        })

        # 執行交易
        if stock_id not in self._positions_cache:
            self._positions_cache[stock_id] = {}

        if stock_id not in self._position_map:
            self._position_map[stock_id] = Position(
                stock_id=stock_id,
                shares=shares,
                entry_date=self._data.current_time,
                avg_price=entry_price
            )
        else:
            self._position_map[stock_id].increase(shares=shares, price=entry_price)

        self._positions_cache[stock_id][self._current_index] = {
            'index': self._current_index,
            'stock_id': stock_id,
            'shares': shares,
            'start_date': self._data.current_time,
            'start_price': entry_price,
        }
        self._balance = after
        self._current_index += 1

        return True

    def sell_all_market(self, stock_id, note=''):
        if stock_id not in self._positions_cache:
            return False

        price = self._data.get_stock_open_price(stock_id)

        for position in self._positions_cache[stock_id].values():
            before = self.current_balance
            fee = self.commission_info.get_sell_commission(price * position['shares'])
            amount = int(position['shares'] * price) - fee
            after = before + amount

            # 先寫 log
            self._trade_logs.append({
                'index': position['index'],
                'date': self._data.current_time.isoformat(),
                'action': 'sell',
                'stock_id': stock_id,
                'shares': position['shares'],
                'fee': fee,
                'price': price,
                'amount': amount,
                'note': note,
            })

            # 執行交易
            self._balance = after

        if stock_id in self._position_map:
            del self._position_map[stock_id]

        del self._positions_cache[stock_id]

        return True

    @property
    def current_balance(self) -> int:
        return self._balance

    @property
    def positions(self) -> [Position]:
        return list(self._position_map.values())

    @property
    def init_balance(self) -> int:
        return self._init_balance

    @property
    def trade_logs(self) -> list:
        return self._trade_logs
