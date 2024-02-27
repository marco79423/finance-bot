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


class StrategyS2V2(StrategyBase):
    """
    新增牛市才買的規則
    """
    name = '策略 S2V2'
    params = dict(
        max_single_position_exposure=0.1,
        sma_short=20,
        sma_long=60,
        sma_out=40,
        mrs_num=120,
        top_mrs_num=50,
        market_over=100
    )
    stabled = True
    available_stock_ids = available_stock_ids

    def init(self, data):
        return dict(
            sma_short=data.close.rolling(window=self.params['sma_short']).mean(),
            sma_long=data.close.rolling(window=self.params['sma_long']).mean(),
            sma_out=data.close.rolling(window=self.params['sma_out']).mean(),
            mrs=data.monthly_revenue / data.monthly_revenue.rolling(window=self.params['mrs_num']).mean(),
            market_over=data.close['0050'] > data.close['0050'].rolling(window=self.params['market_over']).mean(),
        )

    # noinspection PyTypeChecker
    def handle(self):
        sma_short = self.i('sma_short')
        sma_long = self.i('sma_long')
        sma_out = self.i('sma_out')
        mrs = self.i('mrs')
        market_over = self.i('market_over')

        if market_over.iloc[-1]:
            weight_s = mrs.iloc[-1]
            # 過濾權重為 0 的元素
            weight_s = weight_s[weight_s != 0]
            # 根據權重排序
            weight_s = weight_s.sort_values(ascending=False, kind='mergesort')

            # 創建一個初始為 False 的新 Series
            top_mrs = pd.Series(False, index=self.close.index)

            # 將原始 Series 從大到小排序，並選取前 50 個元素的索引
            top_mrs_indices = weight_s.sort_values(ascending=False).iloc[:self.params['top_mrs_num']].index

            # 將這些索引對應的值設置為 True
            top_mrs[top_mrs_indices] = True

            target_list = self.new_target_list([
                (self.current_shares == 0).reindex(self.available_stock_ids, fill_value=True),
                self.close > 10,
                self.close > sma_short.iloc[-1],
                self.close > sma_long.iloc[-1],
                top_mrs,
                ], available_list=self.available_stock_ids)

            target_list = [index for index in top_mrs_indices if index in target_list]
            for stock_id in target_list:
                self.buy_next_day_market(stock_id)

        target_list = self.new_target_list([
            self.close < sma_out.iloc[-1],
        ], available_list=self.broker.holding_stock_ids)
        for stock_id in target_list:
            self.sell_next_day_market(stock_id, note=f'{self.growth_rate[stock_id] * 100:.2f}%')

