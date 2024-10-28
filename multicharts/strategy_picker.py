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


def pick_strategy(filepath):
    data = pd.read_csv(filepath)
    data['Adjusted Calmar Ratio'] = data.apply(adjusted_calmar_ratio, axis=1)
    sorted_data = data.sort_values(by='Adjusted Calmar Ratio', ascending=False)

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
