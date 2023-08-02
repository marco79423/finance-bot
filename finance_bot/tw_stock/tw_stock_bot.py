import datetime as dt
import io
import logging
import random
import time

import pandas as pd
import requests
from fake_useragent import UserAgent
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session

from finance_bot.tw_stock.database import get_engine
from finance_bot.tw_stock.model import TWStockPrice, TWStock
from finance_bot.utility import get_data_folder


class TWStockBot:
    COMMIT_GROUP_SIZE = 1000

    def __init__(self, logger=None):
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger
        self.engine = get_engine()
        self.user_agent = UserAgent()

    def update_stocks(self):
        self.logger.info(f'開始更新台灣股票資訊 ...')
        df = self.crawl_stocks()

        self.logger.info(f'取得 {len(df)} 筆資訊')

        df[['stock_id', 'name']] = df['有價證券代號及名稱'].str.extract(r'([^\s]+)\s+(.*)')
        df = df.drop(columns=['有價證券代號及名稱', '國際證券辨識號碼(ISIN Code)', 'CFICode', '市場別', '備註'])
        df = df.rename(columns={
            '上市日': 'listing_date',
            '產業別': 'industry'
        })

        with Session(self.engine) as session:
            df = df[['stock_id', 'name', 'listing_date', 'industry']]
            df = df[df['stock_id'].notna()]
            self.save_or_update_list(session, TWStock, df)
        self.logger.info('台灣股票資訊更新完成')

    def update_prices_for_date_range(self, start=None, end=None, random_delay=True):
        start = pd.Timestamp(start if start is not None else '2004-01-01')  # 證交所最早只到 2004-01-01
        end = pd.Timestamp(end if end is not None else pd.Timestamp.today().normalize())

        date_range = pd.date_range(start, end, freq='B')
        self.logger.info(f'開始更新 {start:%Y-%m-%d} ~ {end:%Y-%m-%d} 股價資訊 ...')
        for date in reversed(date_range):
            self.update_prices_for_date(date)
            if random_delay:
                delay_seconds = random.randint(1, 10)
                self.logger.info(f'等待 {delay_seconds} 秒 ...')
                time.sleep(delay_seconds)
        self.logger.info(f'{start:%Y-%m-%d}-{end:%Y-%m-%d} 股價資訊更新完成')

    def update_prices_for_date(self, date=None):
        date = pd.Timestamp(date if date is not None else pd.Timestamp.today().normalize())

        self.logger.info(f'開始更新 {date:%Y-%m-%d} 股價資訊 ...')
        raw_df = self.crawl_price(date)
        if raw_df is None or raw_df.empty:
            self.logger.info('沒有股價資訊')
            return
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

        with Session(self.engine) as session:
            df = raw_df.drop(columns=['name'])
            df = df.where(pd.notnull(df), None)  # 將 DataFrame 中的所有 NaN 值轉換為 None
            self.logger.info(f'開始更新共 {len(df)} 筆的股價資訊 ...')
            self.save_or_update_list(session, TWStockPrice, df)

        self.logger.info(f'{date:%Y-%m-%d} 股價資訊更新完成')

    def update_financial_statements(self, stock_id, year, season):
        self.crawl_financial_statements(stock_id, year, season)

    def crawl_stocks(self):
        res = requests.get(
            'https://isin.twse.com.tw/isin/C_public.jsp',
            params={
                'strMode': '2',
            },
            headers={
                'user-agent': self.user_agent.random
            }
        )
        df = pd.read_html(res.text)[0]

        df.columns = df.iloc[0]
        df = df.iloc[2:]
        df = df.dropna(thresh=3, axis=0)
        return df

    def crawl_price(self, date: dt.datetime):
        r = requests.post(
            'https://www.twse.com.tw/exchangeReport/MI_INDEX',
            params={
                'response': 'csv',
                'date': date.strftime('%Y%m%d'),
                'type': 'ALLBUT0999',  # 全部(不含權證、牛熊證、可展延牛熊證)
                '_': int(dt.datetime.now().timestamp() * 1000),
            },
            headers={
                'user-agent': self.user_agent.random
            }
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

    def crawl_financial_statements(self, stock_id, year, season):
        res = requests.get(
            'https://mops.twse.com.tw/server-java/t164sb01',
            params={
                'step': 1,  # 不知啥用的
                'CO_ID': stock_id,
                'SYEAR': year,
                'SSEASON': season,
                'REPORT_ID': 'C',  # 個別財報(A) / 個體財報(B) / 合併報表(C)
            },
            headers={
                'user-agent': self.user_agent.random
            }
        )
        res.encoding = 'big5'
        body = res.text

        data_folder = get_data_folder()
        target_folder = data_folder / 'financial_statements' / stock_id
        target_folder.mkdir(parents=True, exist_ok=True)
        target_file = target_folder / f'{year}Q{season}.html'
        with target_file.open('w', encoding='big5') as fp:
            fp.write(body)

    def save_or_update_list(self, session, model, df):
        for _, group in df.groupby(df.index // self.COMMIT_GROUP_SIZE):
            group.apply(lambda x: self.save_or_update(session, model, x, auto_commit=False), axis=1)
            session.commit()

    @staticmethod
    def save_or_update(session, model, data, auto_commit=True):
        modified = {
            key: value if pd.notnull(value) else None
            for key, value in data.items()
        }

        insert_stmt = insert(model).values(**modified).on_duplicate_key_update(**modified)
        session.execute(insert_stmt)
        if auto_commit:
            session.commit()


if __name__ == '__main__':
    def main():
        logging.basicConfig(
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
            format='[%(asctime)s][%(levelname)s] %(message)s',
        )

        logger = logging.getLogger()
        bot = TWStockBot(logger=logger)
        bot.update_stocks()
        # bot.update_prices_for_date_range('2004-01-01', '2022-02-14')


    main()
