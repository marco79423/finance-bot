import uvicorn
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_trade import TWStockTrade
from finance_bot.infrastructure import infra


class SuperBot(CoreBase):
    name = 'super_bot'

    def __init__(self):
        super().__init__()

        self._telegram_app = self._setup_telegram_app()
        self._tw_stock_trade = TWStockTrade()

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self._telegram_app.initialize()
            await self._telegram_app.start()
            await self._telegram_app.updater.start_polling()

        @app.on_event('shutdown')
        async def shutdown():
            await self._telegram_app.updater.stop()
            await self._telegram_app.stop()
            await self._telegram_app.shutdown()

        uvicorn.run(app, host='0.0.0.0', port=16950)

    def _setup_telegram_app(self):
        token = infra.conf.core.super_bot.telegram.token
        app = Application.builder().token(token).build()
        app.add_handler(CommandHandler("balance", self.command_balance))
        app.add_handler(CommandHandler("trades", self.command_trades))
        return app

    async def command_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = infra.conf.core.super_bot.telegram.chat_id
        if update.message.chat_id == chat_id:
            await update.message.reply_text(f'當前餘額: {self._tw_stock_trade.account_balance} 元')

    async def command_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = infra.conf.core.super_bot.telegram.chat_id
        if update.message.chat_id == chat_id:
            await self._tw_stock_trade.execute_trades()
            await update.message.reply_text(f'執行交易完畢')
