import pandas as pd


def adjusted_calmar_ratio(row):
    net_profit = row['Net Profit']
    max_drawdown = row['Max Intraday Drawdown']
    gross_profit = row['Gross Profit']
    gross_loss = row['Gross Loss']
    total_trades = row['Total Trades']
    win_rate = row['% Profitable'] / 100
    loss_rate = 1 - win_rate
    avg_trade = net_profit / total_trades if total_trades != 0 else 0
    expectancy_component = (gross_profit * win_rate - abs(gross_loss) * loss_rate) / avg_trade if avg_trade != 0 else 0
    adjusted_calmar = (net_profit / -max_drawdown) * expectancy_component if max_drawdown != 0 and net_profit > 0 else 0
    return adjusted_calmar


def pick_strategy(filepath, init_fund=4000000, max_mdd=None, min_trades=None):
    data = pd.read_csv(filepath)
    data['Adjusted Calmar Ratio'] = data.apply(adjusted_calmar_ratio, axis=1)
    data['MDD'] = data['Max Intraday Drawdown'].apply(lambda x: f'{-x / init_fund * 100:.2f}%')
    sorted_data = data.sort_values(by='Adjusted Calmar Ratio', ascending=False)
    if min_trades:
        sorted_data = sorted_data[sorted_data['Total Trades'] >= min_trades]
    if max_mdd:
        sorted_data = sorted_data[-sorted_data['Max Intraday Drawdown'] / init_fund * 100 <= max_mdd]

    exclude_columns = {
        'Gross Profit',
        'Gross Loss',
        'Total Trades',
        '% Profitable',
        'Winning Trades',
        'Losing Trades',
        'Avg Trade',
        'Avg Winning Trade',
        'Avg Losing Trade',
        'Max Consecutive Winners',
        'Max Consecutive Losers',
        'Max Intraday Drawdown',
        'Avg Bars in Winner',
        'Avg Bars in Loser',
        'Return on Account',
        'Profit Factor',
        'Win Loss Ratio',
        'Custom Fitness Value',
    }
    exclude_columns = pd.Series([col for col in sorted_data.columns if col in exclude_columns])

    remaining_columns = sorted_data.drop(columns=exclude_columns).columns
    return sorted_data[remaining_columns]
