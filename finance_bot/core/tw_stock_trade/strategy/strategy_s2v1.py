import pandas as pd
from sqlalchemy import text

from finance_bot.core.tw_stock_trade.strategy.base import StrategyBase
from finance_bot.infrastructure import infra

task_stock_tag_df = pd.read_sql(
    sql=text("SELECT * FROM tw_stock_tag"),
    con=infra.db.engine,
)
df = task_stock_tag_df[task_stock_tag_df['name'] == '個股']
available_stock_ids = df['stock_id'].to_list()


class StrategyS2V1(StrategyBase):
    """第一次上線的版本"""
    name = '策略 S2V1'
    params = dict(
        max_single_position_exposure=0.1,
        sma_short=20,
        sma_long=60,
        mrs_num=90,
    )
    stabled = False
    available_stock_ids = available_stock_ids

    def init(self, data):
        return dict(
            sma_short=data.close.rolling(window=self.params['sma_short']).mean(),
            sma_long=data.close.rolling(window=self.params['sma_long']).mean(),
            mrs_v=data.monthly_revenue / data.monthly_revenue.rolling(window=self.params['mrs_num']).mean(),
        )

    # noinspection PyTypeChecker
    def handle(self):
        sma_short = self.i('sma_short')
        sma_long = self.i('sma_long')
        mrs_v = self.i('mrs_v')

        target_list = self.new_target_list([
            (self.current_shares == 0).reindex(self.available_stock_ids, fill_value=True),
            self.close > 10,
            self.close > sma_short.iloc[-1],
            self.close > sma_long.iloc[-1],
            # self.close > self.open,
            # self.data.close.iloc[-1] > self.data.open.iloc[-1],
            # voc10.iloc[-1] < 100,
        ], available_list=self.available_stock_ids)

        weight_s = mrs_v.iloc[-1]
        # 過濾權重為 0 的元素
        weight_s = weight_s[weight_s != 0]
        # 根據權重排序
        weight_s = weight_s.sort_values(ascending=False, kind='mergesort')

        target_list = [index for index in weight_s.index if index in target_list]
        for stock_id in target_list:
            self.buy_next_day_market(stock_id)

        target_list = self.new_target_list([
            self.close < sma_short.iloc[-1],
            # self.has_profit,
        ], available_list=self.broker.holding_stock_ids)
        for stock_id in target_list:
            self.sell_next_day_market(stock_id, note=f'{self.growth_rate[stock_id] * 100:.2f}%')

        target_list = self.new_target_list([
            # self.close < sma_short.iloc[-1],
            self.today - self.entry_date > pd.Timedelta(days=30),
        ], available_list=self.broker.holding_stock_ids)
        for stock_id in target_list:
            self.sell_next_day_market(stock_id, note=f'{self.growth_rate[stock_id] * 100:.2f}%')
