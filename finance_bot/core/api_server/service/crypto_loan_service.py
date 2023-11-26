from finance_bot.core import CryptoLoan
from finance_bot.infrastructure import infra
from .base import ServiceBase


class CryptoLoanService(ServiceBase):
    name = 'crypto_loan'

    def __init__(self, app):
        super().__init__(app)
        self.crypto_loan = CryptoLoan()

    async def listen(self):
        await infra.mq.subscribe('crypto_loan.lending_task', self.execute_lending_task)
        await infra.mq.subscribe('crypto_loan.send_stats', self.send_stats)

    async def execute_lending_task(self, sub, data):
        await self.execute_task(self.crypto_loan.execute_lending_task, error_message='借錢任務執行失敗')

    async def send_stats(self, sub, data):
        async def get_stats_msg():
            stats = await self.crypto_loan.get_stats()
            return {
                'lending_amount': round(stats.lending_amount, 2),
                'daily_earn': round(stats.daily_earn, 2),
                'average_rate': round(stats.average_rate * 100, 6),
            }

        await self.execute_task(get_stats_msg,
                                success_message='總借出: {lending_amount:.2f}\n預估日收益: {daily_earn:.2f} (平均利率: {average_rate:.6f}%)',
                                error_message='計算統計執行失敗 [{retry_count}]', retries=5)
