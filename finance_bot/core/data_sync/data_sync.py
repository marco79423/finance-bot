import datetime as dt
import io
import random

import asyncio
import pandas as pd
import uvicorn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.core.base import CoreBase
from finance_bot.core.data_sync.market_data import MarketData
from finance_bot.infrastructure import infra
from finance_bot.model import TWStockPrice, TWStock, TWStockMonthlyRevenue, TWStockFinancialStatements


class DataSync(CoreBase):
    name = 'data_sync'

    COMMIT_GROUP_SIZE = 1000

    def __init__(self):
        super().__init__()
        self._market_data = MarketData(logger=self.logger)

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self.listen()

        uvicorn.run(app, host='0.0.0.0', port=16920)

    async def listen(self):
        await infra.mq.subscribe('data_sync.update_tw_stock', self._update_tw_stock_handler)
        await infra.mq.subscribe('data_sync.update_tw_stock_prices', self._update_tw_stock_prices_handler)
        await infra.mq.subscribe('data_sync.update_monthly_revenue', self._update_monthly_revenue_handler)
        await infra.mq.subscribe('data_sync.update_financial_statements', self._update_financial_statements_handler)
        await infra.mq.subscribe('data_sync.update_db_cache', self._update_db_cache_handler)

    async def _update_tw_stock_handler(self, sub, data):
        await self.execute_task(
            '台灣股票資訊更新',
            'data_sync.update_tw_stock',
            self.update_stocks,
            retries=5,
        )

    async def _update_tw_stock_prices_handler(self, sub, data):
        today = pd.Timestamp.today().normalize()
        yesterday = today - pd.Timedelta(days=1)

        await self.execute_task(
            f'{yesterday:%Y-%m-%d} 股價資訊更新',
            'data_sync.update_tw_stock_prices',
            self.update_prices_for_date,
            kargs=dict(date=yesterday),
            retries=5,
        )

    async def _update_monthly_revenue_handler(self, sub, data):
        # 根據規定上市櫃公司營收必須在次月的10號前公告，但遇假期可以延期，如 10 號是週六，可以等下週一才公布
        # 但我想每天都抓應該也不會怎樣
        today = pd.Timestamp.today().normalize()

        # 上個月的同一天
        target_date = today - pd.DateOffset(months=1)
        year, month = target_date.year, target_date.month

        await self.execute_task(
            f'{year}-{month} 月營收財報更新',
            'data_sync.update_monthly_revenue',
            self.update_monthly_revenue,
            kargs=dict(year=year, month=month),
            retries=5,
        )

    async def _update_financial_statements_handler(self, sub, data):
        # 財報公布： 一般公司
        # * 第一季（Q1）法說會：5/15 前
        # * 第二季（Q2）財報：8/14 前
        # * 第三季（Q3）財報：11/14 前
        # * 第四季（Q4）財報及年報：隔年 3/31 前
        #
        # 財報公布： 金融業
        # * 第一季（Q1）財報：5/15 前
        # * 第二季（Q2）財報：8/31 前
        # * 第三季（Q3）財報：11/14 前

        last_period = pd.Period(pd.Timestamp.now(), freq='Q') - 1
        year, quarter = last_period.year, last_period.quarter
        await self.execute_task(
            f'{year}Q{quarter} 財報更新',
            'data_sync.update_financial_statements',
            self.update_all_financial_statements_by_quarter,
            kargs=dict(year=year, quarter=quarter),
            retries=5,
        )

    async def _update_db_cache_handler(self, sub, data):
        await self.execute_task(
            f'台股資料快取更新',
            'data_sync.update_db_cache',
            self.data.rebuild_cache,
            retries=5,
        )

    @property
    def data(self):
        return self._market_data

    async def update_stocks(self):
        self.logger.info(f'開始更新台灣股票資訊 ...')
        df = await self.crawl_stocks()

        total_count = len(df)
        self.logger.info(f'取得 {total_count} 筆資訊')
        async with AsyncSession(infra.db.async_engine) as session:
            await infra.db.batch_insert_or_update(session, TWStock, df)
        self.logger.info('台灣股票資訊更新完成')
        return dict(total_count=total_count)

    async def update_prices_for_date_range(self, start=None, end=None, random_delay=True):
        start = pd.Timestamp(start if start is not None else '2004-01-01')  # 證交所最早只到 2004-01-01
        end = pd.Timestamp(end if end is not None else pd.Timestamp.today().normalize())

        date_range = pd.date_range(start, end, freq='B')
        self.logger.info(f'開始更新 {start:%Y-%m-%d} ~ {end:%Y-%m-%d} 股價資訊 ...')
        for date in reversed(date_range):
            await self.update_prices_for_date(date)
            if random_delay:
                delay_seconds = random.randint(1, 10)
                self.logger.info(f'等待 {delay_seconds} 秒 ...')
                await asyncio.sleep(delay_seconds)
        self.logger.info(f'{start:%Y-%m-%d}-{end:%Y-%m-%d} 股價資訊更新完成')

    async def update_prices_for_date(self, date=None):
        date = pd.Timestamp(date if date is not None else pd.Timestamp.today().normalize())

        self.logger.info(f'開始更新 {date:%Y-%m-%d} 股價資訊 ...')
        raw_df = await self.crawl_price(date)
        if raw_df is None or raw_df.empty:
            self.logger.info('沒有股價資訊')
            return {
                'date': date.isoformat(),
            }
        self.logger.info(f'取得 {len(raw_df)} 筆資訊')

        raw_df = raw_df.rename(columns={
            '證券名稱': 'name',
            "開盤價": "open",
            "最高價": "high",
            "最低價": "low",
            "收盤價": "close",
            "成交股數": "volume",
            "成交金額": "traded_value",
            "成交筆數": "transaction_count",
            "最後揭示買價": "last_bid_price",
            "最後揭示買量": "last_bid_volume",
            "最後揭示賣價": "last_ask_price",
            "最後揭示賣量": "last_ask_volume",
        })

        df = raw_df.drop(columns=['name'])
        df = df.where(pd.notnull(df), None)  # 將 DataFrame 中的所有 NaN 值轉換為 None

        self.logger.info(f'開始更新共 {len(df)} 筆的股價資訊 ...')
        async with AsyncSession(infra.db.async_engine) as session:
            await infra.db.batch_insert_or_update(session, TWStockPrice, df)

        self.logger.info(f'{date:%Y-%m-%d} 股價資訊更新完成')
        return {
            'date': date.isoformat(),
        }

    async def update_all_financial_statements(self, force_update_db=False):
        async with AsyncSession(infra.db.async_engine) as session:
            q = await session.execute(
                select(TWStock)
                .where(TWStock.tracked == True)
                .where(TWStock.instrument_type == '股票')
            )
            for tw_stock in q.scalars():
                await self.update_all_financial_statements_for_stock_id(tw_stock.stock_id, force_update_db)

    async def update_all_financial_statements_by_quarter(self, year, quarter):
        period = pd.Period(f'{year}Q{quarter}')
        self.logger.info(f'更新 {period} 財報 ...')
        async with AsyncSession(infra.db.async_engine) as session:
            q = await session.execute(
                select(TWStock)
                .where(TWStock.tracked == True)
                .where(TWStock.instrument_type == '股票')
            )
            for tw_stock in q.scalars():
                await self.update_financial_statements_for_stock_by_quarter(
                    tw_stock.stock_id,
                    period.year,
                    period.quarter,
                )
        return dict(year=year, quarter=quarter)

    async def update_financial_statements_for_stock_by_quarter(self, stock_id, year, quarter, *, retries=0):
        period = pd.Period(f'{year}Q{quarter}')
        self.logger.info(f'更新 {stock_id} {period} 財報 ...')

        financial_statements_path = await self._get_financial_statements_path(
            stock_id,
            period.year,
            period.quarter
        )

        for i in range(1 + retries):
            try:
                async with AsyncSession(infra.db.async_engine) as session:
                    if not await financial_statements_path.exists():
                        for report_type in ['C', 'A']:
                            ok = await self._download_financial_statements(
                                stock_id, period.year,
                                period.quarter,
                                report_type,
                                financial_statements_path
                            )
                            if ok:
                                break
                        if not ok:
                            self.logger.info(f'沒抓到 {stock_id} {period} 財報 ...')
                            await financial_statements_path.unlink(missing_ok=True)
                            return

                    data = await self._parse_financial_statements(year, financial_statements_path)
                    if data:
                        data = {
                            'stock_id': stock_id,
                            'date': f'{year}Q{quarter}',
                            **data,
                        }
                        await infra.db.insert_or_update(session, TWStockFinancialStatements, data)
                    break
            except Exception as e:
                self.logger.exception(f'更新 {stock_id} {period} 財報失敗，等待重試中... :')
                if i < 1 + retries:
                    self.logger.info(f'更新 {stock_id} {period} 財報失敗，等待重試中... :{str(e)}')
                    await asyncio.sleep(60)
                else:
                    raise e

    async def update_all_financial_statements_for_stock_id(self, stock_id, force_update_db=False):
        self.logger.info(f'更新 {stock_id} 所有財報 ...')
        async with AsyncSession(infra.db.async_engine) as session:
            q = await session.execute(
                select(TWStock.listing_date)
                .where(TWStock.stock_id == stock_id)
                .limit(1)
            )
            date, = q.first()

            excluded_periods = []
            if not force_update_db:
                q = await session.execute(
                    select(TWStockFinancialStatements.date)
                    .where(TWStockFinancialStatements.stock_id == stock_id)
                )
                for date in q.scalars():
                    excluded_periods.append(pd.Period(date))

        start_date = max(pd.Timestamp(date), pd.Timestamp('2013'))
        periods = pd.period_range(
            pd.Period(start_date, freq='Q'),
            pd.Period(pd.Timestamp.now(), freq='Q') - 1,  # 上一季
            freq='Q',
        )
        periods = periods[~periods.isin(excluded_periods)]

        for period in periods:
            await self.update_financial_statements_for_stock_by_quarter(stock_id, period.year, period.quarter)

    @staticmethod
    async def crawl_stocks():
        res = await infra.api.get(
            'https://isin.twse.com.tw/isin/C_public.jsp',
            params={
                'strMode': '2',
            },
        )
        df = pd.read_html(res.text)[0]
        df.columns = df.iloc[0]

        df['instrument_type'] = df.iloc[:, 6].fillna(method='ffill')
        df = df.iloc[1:, ]
        df = df[df['有價證券代號及名稱'] != df['國際證券辨識號碼(ISIN Code)']]
        df[['stock_id', 'name']] = df['有價證券代號及名稱'].str.extract(r'([^\s]+)\s+(.*)')
        df = df.drop(columns=['有價證券代號及名稱', '國際證券辨識號碼(ISIN Code)', 'CFICode', '市場別', '備註'])
        df = df.rename(columns={
            '上市日': 'listing_date',
            '產業別': 'industry'
        })
        return df

    @staticmethod
    async def crawl_price(date: dt.datetime):
        r = await infra.api.post(
            'https://www.twse.com.tw/exchangeReport/MI_INDEX',
            params={
                'response': 'csv',
                'date': date.strftime('%Y%m%d'),
                'type': 'ALLBUT0999',  # 全部(不含權證、牛熊證、可展延牛熊證)
                '_': int(dt.datetime.now().timestamp() * 1000),
            },
        )

        content = r.text.replace('=', '')  # 例子： ="0050"

        # 將 column 數量小於等於 10 的行數都刪除
        lines = content.split('\n')
        lines = list(filter(lambda l: len(l.split('",')) > 10, lines))

        # 將每一行再合成同一行，並用肉眼看不到的換行符號'\n'分開
        content = "\n".join(lines)

        # 假如沒下載到，則回傳None（代表抓不到資料）
        if content == '':
            return None

        df = pd.read_csv(io.StringIO(content))
        df = df.astype(str)
        df = df.apply(lambda s: s.str.replace(',', ''))

        df = df.rename(columns={
            '證券代號': 'stock_id',
        })
        df = df.drop([
            '漲跌價差',
            '本益比'
        ], axis=1)

        # 將所有的表格元素(除了 stock_id 和名稱)都轉換成數字 (error='coerce' 代表無法轉成數字則用 NaN 取代)
        df = df.apply(lambda s: pd.to_numeric(s, errors='coerce') if s.name not in ['stock_id', '證券名稱'] else s)

        # 刪除不必要的欄位
        df = df[df.columns[df.isnull().all() == False]]

        df['date'] = pd.to_datetime(date)

        return df

    async def update_monthly_revenue(self, year, month):
        self.logger.info(f'開始更新月財報資訊 ...')

        if year < 2012:
            raise ValueError('最早只到 2012 年 1 月 (民國 101 年)')
        if year == 2012:
            raise ValueError('2012 年都沒有 CSV，所以懶得處理')

        listing_status = 'sii'  # sii: 上市公司, otc: 上櫃公司, rotc: 興櫃公司, pub: 公開發行公司
        company_type = 0  # 0: 國內公司, 1: 國外 KY 公司

        url = 'https://mops.twse.com.tw/server-java/FileDownLoad'
        res = await infra.api.post(
            url,
            data={
                'step': 9,  # 不知啥用的
                'functionName': 'show_file2',
                'filePath': f'/t21/{listing_status}/',
                'fileName': f't21sc03_{year - 1911}_{month}.csv',
            },
        )

        res.encoding = 'utf-8'  # HTTPX 自動偵測編碼會錯誤
        df = pd.read_csv(io.StringIO(res.text))

        df = df[['公司代號', '營業收入-當月營收']]
        df = df.rename(columns={
            '公司代號': 'stock_id',
            '營業收入-當月營收': 'revenue',
        })
        df['date'] = f'{year}-{month:02}'
        async with AsyncSession(infra.db.async_engine) as session:
            await infra.db.batch_insert_or_update(session, TWStockMonthlyRevenue, df)

        url = f'https://mops.twse.com.tw/nas/t21/{listing_status}/t21sc03_{year - 1911}_{month}_{company_type}.html'

        res = await infra.api.get(url)
        res.encoding = 'big5'
        body = res.text

        target_folder = infra.path.data_folder / 'monthly_revenue'
        await target_folder.mkdir(parents=True, exist_ok=True)
        target_file = target_folder / f'{year}_{month}.html'
        async with target_file.open('w', encoding='utf-8') as fp:
            await fp.write(body)

        self.logger.info(f'更新月財報資訊完成')
        return dict(year=year, month=month)

    @staticmethod
    async def _get_financial_statements_path(stock_id, year, quarter):
        target_folder = infra.path.data_folder / 'financial_statements' / stock_id
        await target_folder.mkdir(parents=True, exist_ok=True)
        target_path = target_folder / f'{year}Q{quarter}.html'
        return target_path

    async def _download_financial_statements(self, stock_id, year, quarter, report_type, dest_path):
        if year < 2013:
            raise ValueError('2013  (民國 102 年) 前不處理')
        if report_type not in ['A', 'B', 'C']:
            raise ValueError('不支援的 Report type (A：個別財報 / B：個體財報 / C：合併報表)')

        self.logger.info(f'下載 {stock_id} 報表中 ...')
        res = await infra.api.get(
            'https://mops.twse.com.tw/server-java/t164sb01',
            params={
                'step': 1,  # 不知啥用的
                'CO_ID': stock_id,
                'SYEAR': year,
                'SSEASON': quarter,
                'REPORT_ID': report_type,  # 個別財報(A) / 個體財報(B) / 合併報表(C)
            },
            cooling_time=dt.timedelta(seconds=6)
        )
        res.encoding = 'big5'
        body = res.text
        async with dest_path.open('w', encoding='utf-8') as fp:
            await fp.write(body)

        for pattern in ['查無資料', '檔案不存在']:
            if pattern in body:
                return False
        return True

    async def _parse_financial_statements(self, year, source_path):
        async with source_path.open('r', encoding='utf-8') as fp:
            body = await fp.read()

        if year < 2019:
            dfs = pd.read_html(io.StringIO(body))
            if len(dfs) < 2:
                return None
            df = dfs[1]
            df = df.iloc[:, :2]
            df.columns = ['name', 'value']
            df['value'] = pd.to_numeric(df['value'], 'coerce')
            df = df.dropna()
            df = df.set_index('name')

            return {
                'share_capital': df['value'].loc['股本合計'],
            }
        else:
            try:
                dfs = pd.read_html(io.StringIO(body))
                df = dfs[0]
                df = df.iloc[:, :3]
                df.columns = ['code', 'name', 'value']
                df = df.set_index('code')
                df['value'] = pd.to_numeric(df['value'], 'coerce')
                df = df.dropna()

                # 金融保險業 (如 5876) 是 31100
                share_capital = self._get_df_value(df, ['3100', '31100'])

                return {
                    'share_capital': share_capital,
                }
            except ValueError:
                return None

    @staticmethod
    def _get_df_value(df, possible_indexes, column_name='value'):
        value = None
        for possible_index in possible_indexes:
            if value is None:
                try:
                    value = df.at[possible_index, column_name]
                except KeyError:
                    pass
        return value


if __name__ == '__main__':
    def main():
        bot = DataSync()
        # bot.update_stocks()
        # bot.update_prices_for_date_range('2004-01-01', '2022-02-14')
        # for d in pd.date_range('2014-07', '2023-07', freq='MS'):
        #     print(f'{d.year}-{d.month:02}')
        #     bot.update_monthly_revenue(year=d.year, month=d.month)
        #     time.sleep(30)
        bot.update_all_financial_statements_for_stock_id('2330')
        bot.update_all_financial_statements_by_quarter(2022, 1)


    main()
