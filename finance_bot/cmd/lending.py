import asyncio

import click

from finance_bot.core import LendingBot


def create_lending_cli():
    @click.group('lending')
    def lending():
        """放貸"""
        pass

    @lending.command('records')
    def get_records():
        lending_bot = LendingBot()
        records = asyncio.run(lending_bot.get_lending_records())
        for record in sorted(records, key=lambda r: r.end):
            print('金額：{amount:.2f}\t利率：{current_rate:.6f}%\t到期 {end}\t剩下 {last_time}'.format(**record.json()))

    return lending
