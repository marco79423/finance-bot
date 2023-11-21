import pandas as pd
import pytest

from . import data_adapter


@pytest.fixture
def mock_get_stock_prices_df(mocker):
    return mocker.patch.object(data_adapter, 'get_stock_prices_df', return_value=pd.DataFrame({
        'stock_id': ['a'] * 10,
        'open': list(range(1, 11)),
        'close': list(range(1, 11)),
        'high': list(range(1, 11)),
        'low': list(range(1, 11)),
        'volume': list(range(1, 11)),
    }, index=pd.date_range('2023-01-01', periods=10, freq='D')))


@pytest.mark.parametrize("start_time, expected_start_time", [
    (None, pd.Timestamp('2023-01-01')),
    ('2023-01-01', pd.Timestamp('2023-01-01')),
    (pd.Timestamp('2023-01-05'), pd.Timestamp('2023-01-05')),
    ('2023-01-10', pd.Timestamp('2023-01-10')),
    ('2022-12-31', pd.Timestamp('2022-12-31')),
    ('2023-01-11', pd.Timestamp('2023-01-11')),
])
def test_start_time_with_different_start_time(mock_get_stock_prices_df, start_time, expected_start_time):
    adapter = data_adapter.DataAdapter(start=start_time)
    assert adapter.start_time == pd.Timestamp(expected_start_time)
