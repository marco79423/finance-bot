import abc
from typing import Optional, List

from tool.backtester.model import LimitData


class StrategyBase(abc.ABC):
    name: str
    params: dict = {}
    data: LimitData
    available_stock_ids: Optional[List[str]] = None

    _buy_next_day_market = False
    _sell_next_day_market = False

    @abc.abstractmethod
    def handle(self):
        pass

    def buy_next_day_market(self, confident_score=1):
        """
        在隔天市價買入 (但在回測試會以買在最高價計算)
        :param confident_score:
        :return:
        """
        self._buy_next_day_market = True

    def sell_next_day_open(self):
        """
        在隔天市價賣出 (但在回測時會以賣在最低價計算)
        :return:
        """
        self._sell_next_day_market = True

    def inter_clean(self):
        self._buy_next_day_market = False
        self._sell_next_day_market = False
