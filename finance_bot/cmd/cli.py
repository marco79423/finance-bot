import IPython
import click
import requests

from finance_bot.cmd.data_sync import create_data_sync_cli
from finance_bot.cmd.crypto_loan import create_crypto_loan_cli
from finance_bot.cmd.schedule import create_schedule_cli
from finance_bot.core.shell.config import get_config


def create_cli():
    @click.group()
    def cli():
        """兩大類專用理財小工具"""
        pass

    @cli.command('ping')
    @click.option('--url', default='http://localhost:16888', help='理財機器人的 URL')
    def ping(url):
        try:
            resp = requests.get(f'{url}/debug/ping')
            print(resp.text)
        except requests.exceptions.RequestException:
            print(f'理財機器人 ({url}) 連線失敗')

    @cli.command('shell', short_help='啟動理財機器人 Shell')
    @click.option('--url', default='http://localhost:16888', help='理財機器人的 URL')
    def shell(url):
        c = get_config(url)
        IPython.start_ipython(header='理財機器人 Shell', config=c, argv=[])

    cli.add_command(create_schedule_cli())
    cli.add_command(create_crypto_loan_cli())
    cli.add_command(create_data_sync_cli())

    return cli
