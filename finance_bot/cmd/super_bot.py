import traceback

import asyncio
import click
import rich

from finance_bot.core.super_bot import SuperBot


def create_super_bot_cli():
    @click.group('super_bot')
    def super_bot():
        """機器人"""
        pass

    sb = SuperBot()

    @super_bot.command("start")
    def start_server():
        """啟動服務"""
        sb.start()

    @super_bot.command("daily_status")
    def send_daily_status():
        """傳送最新狀態"""
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(sb.send_daily_status())
            rich.print('傳送完畢')
        except:
            rich.print(traceback.format_exc())

    return super_bot
