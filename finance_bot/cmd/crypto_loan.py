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
    def start_server():
        """啟動服務"""
        cl.start()

    @crypto_loan.command('records')
    def get_records():
        records = asyncio.run(cl.get_lending_records())
        for record in sorted(records, key=lambda r: r.end):
            print('金額：{amount:.2f}\t利率：{current_rate:.6f}%\t到期 {end}\t剩下 {last_time}'.format(**record.json()))

    @crypto_loan.command('status')
    def get_records():
        status = asyncio.run(cl.get_stats())
        status = {
            **status,
            'average_rate': status['average_rate'] * 100
        }

        print('總借出: {lending_amount:.2f}'.format(**status))
        print('預估日收益: {daily_earn:.2f} (平均利率: {average_rate:.6f}%)'.format(**status))

    return crypto_loan
