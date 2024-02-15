import json

import pandas as pd
import uvicorn
from sqlalchemy import text
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler

from finance_bot.core.base import CoreBase
from finance_bot.core.schedule import Schedule
from finance_bot.core.tw_stock_trade import TWStockTrade
from finance_bot.infrastructure import infra


class SuperBot(CoreBase):
    name = 'super_bot'

    def __init__(self):
        super().__init__()

        self._telegram_app = self._setup_telegram_app()
        self._tw_stock_trade = TWStockTrade()
        self._schedule = Schedule()

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self._listen()
            await self._start_telegram_app()

        @app.on_event('shutdown')
        async def shutdown():
            await self._telegram_app.updater.stop()
            await self._telegram_app.stop()
            await self._telegram_app.shutdown()

        uvicorn.run(app, host='0.0.0.0', port=16950)

    async def _listen(self):
        await infra.mq.subscribe('super_bot.send_daily_status', self._send_daily_status_handler)

    async def _start_telegram_app(self):
        await self._telegram_app.initialize()
        await self._telegram_app.start()
        await self._telegram_app.updater.start_polling()

    def _setup_telegram_app(self):
        token = infra.conf.core.super_bot.telegram.token
        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("balance", self.command_balance))
        app.add_handler(CommandHandler("strategy", self.command_strategy))
        app.add_handler(CommandHandler("trades", self.command_trades))
        app.add_handler(CommandHandler("schedule", self.command_schedule))
        app.add_handler(CallbackQueryHandler(self.handle_schedule_command))
        return app

    async def _send_daily_status_handler(self, sub, data):
        await self.send_daily_status()

    async def send_daily_status(self):
        task_status_df = pd.read_sql(
            sql=text("SELECT * FROM task_status"),
            con=infra.db.engine,
            index_col='key',
            parse_dates=['created_at', 'updated_at'],
            dtype={
                'is_error': bool,
            }
        )

        # 狀態
        if task_status_df['is_error'].any():
            status_msg = '出現異常\n'
        else:
            status_msg = '一切看起來都 ok\n'

        # 項目
        items_msg = ''

        # 加密放貸
        keys = [
            'crypto_loan.update_status'
        ]
        if task_status_df.index.isin(keys).any():
            items_msg += '加密放貸:\n'

            key = 'crypto_loan.update_status'
            if key in task_status_df.index:
                row = task_status_df.loc[key]
                if row['is_error']:
                    items_msg += '異常\n'
                else:
                    result = json.loads(row['detail'])
                    result = {
                        **result,
                        'average_rate': result['average_rate'] * 100
                    }
                    items_msg += '總借出: {lending_amount:.2f}\n預估日收益: {daily_earn:.2f} (平均利率: {average_rate:.6f}%)\n'.format(
                        **result
                    )

            items_msg += '\n'

        # 資料同步
        keys = [
            'data_sync.update_tw_stock',
            'data_sync.update_tw_stock_prices',
            'data_sync.update_monthly_revenue',
            'data_sync.update_financial_statements',
            'data_sync.update_db_cache',
        ]
        if task_status_df.index.isin(keys).any():
            items_msg += '資料同步:\n'

            key = 'data_sync.update_tw_stock'
            if key in task_status_df.index:
                row = task_status_df.loc[key]
                if row['is_error']:
                    items_msg += '台灣股票資訊更新失敗\n'.format(**json.loads(row['detail']))
                else:
                    items_msg += '台灣股票資訊更新完畢 ({total_count}筆)\n'.format(**json.loads(row['detail']))

            key = 'data_sync.update_tw_stock_prices'
            if key in task_status_df.index:
                row = task_status_df.loc[key]
                if row['is_error']:
                    items_msg += '台灣股價更新失敗\n'
                else:
                    result = json.loads(row['detail'])
                    date = pd.Timestamp(result['date'])
                    items_msg += f'{date:%Y-%m-%d} 台灣股價更新完畢\n'

            key = 'data_sync.update_monthly_revenue'
            if key in task_status_df.index:
                row = task_status_df.loc[key]
                if row['is_error']:
                    items_msg += '月營收財報更新失敗\n'
                else:
                    items_msg += '{year}-{month} 月營收財報更新完畢\n'.format(**json.loads(row['detail']))

            key = 'data_sync.update_financial_statements'
            if key in task_status_df.index:
                row = task_status_df.loc[key]
                if row['is_error']:
                    items_msg += '財報更新失敗\n'
                else:
                    items_msg += '{year}Q{quarter} 財報更新完畢\n'.format(**json.loads(row['detail']))

            key = 'data_sync.update_db_cache'
            if key in task_status_df.index:
                row = task_status_df.loc[key]
                if row['is_error']:
                    items_msg += '台股資料快取更新失敗\n'
                else:
                    items_msg += '台股資料快取更新完畢\n'
            items_msg += '\n'

        # 預計執行
        actions_msg = ''

        key = 'tw_stock_trade.update_strategy_actions'
        if key in task_status_df.index:
            row = task_status_df.loc[key]
            if row['is_error']:
                actions_msg = '異常\n'
            else:
                actions = json.loads(row['detail'])
                if actions:
                    for action in actions:
                        if action['operation'] == 'buy':
                            actions_msg += '買 {stock_id} {shares} 股 參考價: {price} (理由：{note})\n'.format(**action)
                        if action['operation'] == 'sell':
                            actions_msg += '賣 {stock_id} {shares} 股 參考價: {price} (理由：{note})\n'.format(**action)
                else:
                    actions_msg = '沒有\n'

        message = "狀態：\n{status}\n項目：\n{items}\n預計執行：\n{actions}"
        message = message.format(
            status=status_msg,
            items=items_msg,
            actions=actions_msg,
        )

        await infra.notifier.send(message)

    async def command_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = infra.conf.core.super_bot.telegram.chat_id
        if update.message.chat_id == chat_id:
            await update.message.reply_text(f'當前餘額: {self._tw_stock_trade.account_balance} 元')

    @staticmethod
    async def command_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = infra.conf.core.super_bot.telegram.chat_id
        if update.message.chat_id == chat_id:
            await infra.mq.publish('tw_stock_trade.update_strategy_actions', {})

    @staticmethod
    async def command_trades(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = infra.conf.core.super_bot.telegram.chat_id
        if update.message.chat_id == chat_id:
            await infra.mq.publish('tw_stock_trade.execute_trades', {})

    async def command_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = infra.conf.core.super_bot.telegram.chat_id
        if update.message.chat_id == chat_id:
            keyboard = [
                [InlineKeyboardButton(task_key, callback_data=task_key)]
                for task_key in self._schedule.task_keys
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text("選擇一項:", reply_markup=reply_markup)

    async def handle_schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        await query.answer()

        await self._schedule.send_task(query.data)
