import dataclasses
import datetime as dt

import bfxapi
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.core.base import CoreBase
from finance_bot.infrastructure import infra
from finance_bot.repository import SettingCryptoLoanRepository


@dataclasses.dataclass
class FundingStrategy:
    f_type: str
    rate: float
    period: int

    def is_used_by(self, offer: bfxapi.FundingOffer):
        return (
                self.f_type == offer.f_type and
                self.rate == offer.rate and
                self.period == offer.period
        )


@dataclasses.dataclass
class LendingRecord:
    time: dt.datetime
    current_rate: float
    amount: float
    period: dt.timedelta
    start: dt.datetime
    end: dt.datetime

    @property
    def daily_earn(self):
        return self.current_rate * self.amount

    def json(self):
        return {
            'current_rate': self.current_rate,
            'amount': self.amount,
            'daily_earn': self.daily_earn,
            'period': self.period,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'last_time': str(self.end - infra.time.get_now())
        }


class CryptoLoan(CoreBase):
    name = 'crypto_loan'

    BITFINEX_FEES = 0.15

    MAX_OFFER_AMOUNT = 1000
    MIN_RATE = 0.0001
    MIN_RATE_INCR_PER_DAY = 0.00003
    POSSIBLE_PERIOD = (2, 3, 4, 5, 6, 7, 8, 10, 14, 15, 16, 20, 21, 22, 24, 30)

    def __init__(self):
        super().__init__()

        self._client = bfxapi.Client(
            API_KEY=infra.conf.core.crypto_loan.api_key,
            API_SECRET=infra.conf.core.crypto_loan.api_secret,
        )

        self._setting_repo = SettingCryptoLoanRepository()

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')

        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self.listen()
            await self.start_jobs()

        uvicorn.run(app, host='0.0.0.0', port=16910)

    async def listen(self):
        await infra.mq.subscribe('crypto_loan.update_status', self._update_status_handler)

    async def start_jobs(self):
        infra.scheduler.add_task(
            self._execute_lending_task,
            'interval',
            minutes=10,
        )

    async def _update_status_handler(self, sub, data):
        await self.execute_task(
            f'放貨狀態更新',
            'crypto_loan.update_status',
            self.get_stats,
            retries=5,
        )

    async def _execute_lending_task(self):
        strategy = await self.make_strategy()
        reserve_amount = await self.get_reserve_amount()

        # 取消所有不同策略的訂單
        offers = await self._client.rest.get_funding_offers(symbol='fUSD')
        for offer in offers:
            if offer.f_type == bfxapi.FundingOffer.Type.FRR_DELTA:
                continue

            if not strategy.is_used_by(offer):
                await self._client.rest.submit_cancel_funding_offer(offer.id)
                self.logger.info(f'[{dt.datetime.now()}] 取消訂單 {offer}')

        # 如果錢包有錢但是小於 150，取消金額最小的訂單
        balance_available = await self.get_funding_balance()
        if 1 < balance_available < 150:
            offers = await self._client.rest.get_funding_offers(symbol='fUSD')

            min_amount_offer = None
            for offer in offers:
                if offer.f_type == bfxapi.FundingOffer.Type.FRR_DELTA:
                    continue

                if min_amount_offer is None or offer.amount < min_amount_offer.amount:
                    min_amount_offer = offer

            if min_amount_offer:
                await self._client.rest.submit_cancel_funding_offer(min_amount_offer.id)
                self.logger.info(f'[{dt.datetime.now()}] 取消訂單 {min_amount_offer}')

        # 根據當前餘額和策略下訂單
        frr_rate = await self.get_frr_rate()
        balance_available = await self.get_funding_balance()

        if reserve_amount:
            balance_available -= reserve_amount

        while balance_available >= 150:
            amount = self.MAX_OFFER_AMOUNT
            if balance_available - self.MAX_OFFER_AMOUNT < 150:
                amount = balance_available

            # 如果 FRR 比較好，而且沒有 FRR 的訂單，優先 FRR
            if strategy.rate < frr_rate and not await self.has_frr_offer():
                resp = await self._client.rest.submit_funding_offer(
                    symbol='fUSD',
                    amount=amount,
                    rate=0,
                    period=30,
                    funding_type=bfxapi.FundingOffer.Type.FRR_DELTA
                )
                self.logger.info(f'[{dt.datetime.now()}] 新增 FRR 訂單 {resp.notify_info} (金額：{amount})')
            else:
                resp = await self._client.rest.submit_funding_offer(
                    symbol='fUSD',
                    amount=amount,
                    rate=strategy.rate,
                    period=strategy.period,
                    funding_type=strategy.f_type
                )
                self.logger.info(f'[{dt.datetime.now()}] 新增訂單 {resp.notify_info} (金額：{amount})')
            balance_available -= amount

    async def get_lending_records(self):
        """取得當下的借貸資訊"""
        now = infra.time.get_now()
        frr_rate = await self.get_frr_rate()

        lending_credits = []
        for credit in await self._client.rest.get_funding_credits(symbol='fUSD'):
            rate = credit.rate

            # 如果 rate = 0 就當 FRR
            if rate == 0:
                rate = frr_rate

            lending_credits.append(LendingRecord(
                time=now,
                current_rate=rate,
                amount=credit.amount,
                period=credit.period,
                start=infra.time.from_milli_timestamp(credit.mts_opening),
                end=infra.time.from_milli_timestamp(credit.mts_opening) + dt.timedelta(days=credit.period),
            ))
        return lending_credits

    async def get_stats(self):
        lending_amount = 0
        daily_earn = 0
        for credit_record in await self.get_lending_records():
            lending_amount += credit_record.amount
            daily_earn += credit_record.daily_earn

        if lending_amount != 0:
            average_rate = daily_earn / lending_amount
        else:
            average_rate = 0

        return {
            'lending_amount': lending_amount,
            'daily_earn': daily_earn * (1 - self.BITFINEX_FEES),
            'average_rate': average_rate,
        }

    async def make_strategy(self):
        start = int((dt.datetime.now() - dt.timedelta(hours=1)).timestamp() * 1000)
        possible_rates = []

        # 找出最小可接受利率
        min_rate = await self.get_highest_rate(2, '5m', start=start)
        if not min_rate or min_rate < self.MIN_RATE:
            min_rate = self.MIN_RATE

        for period in self.POSSIBLE_PERIOD:
            rate = await self.get_highest_rate(period, '5m', start=start)
            if rate and rate >= min_rate + (period - 2) * self.MIN_RATE_INCR_PER_DAY:
                possible_rates.append((self.get_annual_rate(rate, period), period, rate))

        if not possible_rates:
            self.logger.info('沒找到最佳利率，掛最低利率')
            return FundingStrategy(
                f_type=bfxapi.FundingOffer.Type.LIMIT,
                rate=min_rate,
                period=2,
            )

        possible_rates.sort(reverse=True)
        _, acceptable_period, acceptable_rate = possible_rates[0]

        # print('從下面可選利率選出第一個為最佳利率')
        # for annual_rate, period, rate in possible_rates:
        #     print(f'週期: {period} 利率: {rate} (計算年利率: {annual_rate})')

        return FundingStrategy(
            f_type=bfxapi.FundingOffer.Type.LIMIT,
            rate=acceptable_rate,
            period=acceptable_period,
        )

    async def get_frr_rate(self):
        [frr_rate, *_] = await self._client.rest.get_public_ticker('fUSD')
        return frr_rate

    async def get_highest_rate(self, period, timeframe, start=None, end=None):
        highest_rate = None

        candles = await self._client.rest.get_public_candles(f'fUSD:p{period}', start=start, end=end, tf=timeframe)
        for candle in candles:
            [mts, open, close, high, low, volume] = candle
            if volume > 0:
                if highest_rate is None or high > highest_rate:
                    highest_rate = high
        return highest_rate

    async def get_funding_balance(self):
        wallets = await self._client.rest.get_wallets()
        for wallet in wallets:
            if wallet.type == 'funding' and wallet.currency == 'USD':
                return wallet.balance_available

    async def has_frr_offer(self):
        offers = await self._client.rest.get_funding_offers(symbol='fUSD')
        for offer in offers:
            if offer.f_type == bfxapi.FundingOffer.Type.FRR_DELTA:
                return True
        return False

    async def get_total_asset(self):
        wallets = await self._client.rest.get_wallets()
        for wallet in wallets:
            if wallet.type == 'funding' and wallet.currency == 'USD':
                return wallet.balance

    async def get_min_amount_offer(self):
        offers = await self._client.rest.get_funding_offers(symbol='fUSD')

        min_amount_offer = None
        for offer in offers:
            if min_amount_offer is None or offer.amount < min_amount_offer.amount:
                min_amount_offer = offer
        return min_amount_offer

    @staticmethod
    def get_annual_rate(rate, period):
        return (1 + rate * period) ** (365 / period) - 1

    async def get_reserve_amount(self):
        async with AsyncSession(infra.db.async_engine) as session:
            amount = await self._setting_repo.get_reserve_amount(session)
            return float(amount)
