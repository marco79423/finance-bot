import click

from finance_bot.core.super_bot import SuperBot


def create_super_bot_cli():
    @click.group('super_bot')
    def super_bot():
        """機器人"""
        pass

    sb = SuperBot()

    @super_bot.command("start")
    def start():
        """啟動服務"""
        sb.start()

    return super_bot
