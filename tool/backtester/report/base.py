import abc
import dataclasses

from tool.backtester.broker import Broker


@dataclasses.dataclass
class ReportBase:
    strategy_name: str
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
        return self.broker.start_date

    @property
    def end(self):
        return self.broker.current_date

    @property
    def trades(self):
        return self.broker.analysis_trades

    @property
    def trade_logs(self):
        return self.broker.trade_logs

    @abc.abstractmethod
    def show(self):
        pass
