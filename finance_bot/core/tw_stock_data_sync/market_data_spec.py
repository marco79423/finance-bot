import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from finance_bot.core.tw_stock_data_sync import market_data


@pytest.fixture
def mock_get_stock_prices_df(mocker):
    prices = []
    for stock_id in ['1000', '2000', '3000']:
        for i in range(10):
            prices.append({
                'stock_id': stock_id,
                'open': 5,
                'close': 6,
                'high': 10,
                'low': 1,
                'volume': 1000,
                'date': pd.Timestamp('2023-01-01') + pd.Timedelta(days=i)
            })
    stock_prices_df = pd.DataFrame(prices).set_index('date').sort_index()
    return mocker.patch.object(market_data, 'get_stock_prices_df', return_value=stock_prices_df)


# @pytest.mark.parametrize("start_time, expected_start_time", [
#     (None, pd.Timestamp('2023-01-01')),
#     ('2023-01-01', pd.Timestamp('2023-01-01')),
#     (pd.Timestamp('2023-01-05'), pd.Timestamp('2023-01-05')),
#     ('2023-01-10', pd.Timestamp('2023-01-10')),
#     ('2022-12-31', pd.Timestamp('2022-12-31')),
#     ('2023-01-11', pd.Timestamp('2023-01-11')),
# ])
# def test_start_time_with_different_start_time(mock_get_stock_prices_df, start_time, expected_start_time):
#     adapter = market_data.MarketData(start=start_time)
#     assert adapter.start_time == pd.Timestamp(expected_start_time)


def test_close(mock_get_stock_prices_df):
    expected_df = pd.DataFrame({
        '1000': [1000] * 10,
        '2000': [1000] * 10,
        '3000': [1000] * 10,
    }, index=pd.date_range('2023-01-01', periods=10, freq='D', name='date'),
        columns=pd.Series(['1000', '2000', '3000'], name='stock_id'))

    data = market_data.MarketData()
    assert_frame_equal(data.volume, expected_df, check_freq=False)


def test_volume(mock_get_stock_prices_df):
    expected_df = pd.DataFrame({
        '1000': [6] * 10,
        '2000': [6] * 10,
        '3000': [6] * 10,
    }, index=pd.date_range('2023-01-01', periods=10, freq='D', name='date'),
        columns=pd.Series(['1000', '2000', '3000'], name='stock_id'))

    data = market_data.MarketData()
    assert_frame_equal(data.close, expected_df, check_freq=False)
