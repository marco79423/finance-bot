import abc
import dataclasses

from tool.backtester.broker import Broker
from tool.backtester.data_source import StockDataSource


@dataclasses.dataclass
class ReportBase:
    strategy_name: str
    data_source: StockDataSource
    broker: Broker

    @property
    def init_funds(self):
        return self.broker.init_funds

    @property
    def final_funds(self):
        return self.broker.funds

    @property
    def final_equity(self):
        return self.broker.current_equity

    @property
    def start(self):
        return self.data_source.start_time

    @property
    def end(self):
        return self.data_source.current_time

    @property
    def trades(self):
        return self.broker.analysis_trades

    @property
    def trade_logs(self):
        return self.broker.trade_logs

    @property
    def account_balance_logs(self):
        return self.broker.account_balance_logs

    @abc.abstractmethod
    def show(self):
        pass
