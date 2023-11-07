import dataclasses
from typing import List

import pandas as pd


@dataclasses.dataclass
class Result:
    strategy_name: str
    init_funds: int
    final_funds: int
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    trade_logs: List[dict]

    account_balance_logs: List[dict]
    trades: pd.DataFrame
    equity_curve: pd.Series
    final_equity: float
    total_return: int
    total_return_with_fee: int
    total_return_rate_with_fee: float
    annualized_return_rate_with_fee: float
