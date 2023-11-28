import asyncio

import click

from finance_bot.core import CryptoLoan


def create_crypto_loan_cli():
    @click.group('crypto_loan')
    def crypto_loan():
        """放貸"""
        pass

    cl = CryptoLoan()

    @crypto_loan.command("start")
    def start():
        """啟動服務"""
        cl.start()

    @crypto_loan.command('records')
    def get_records():
        records = asyncio.run(cl.get_lending_records())
        for record in sorted(records, key=lambda r: r.end):
            print('金額：{amount:.2f}\t利率：{current_rate:.6f}%\t到期 {end}\t剩下 {last_time}'.format(**record.json()))

    return crypto_loan
