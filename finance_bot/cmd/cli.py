import click
import requests

from finance_bot.server.api_server import APIServer


def create_cli():
    @click.group()
    def cli():
        """兩大類專用理財小工具"""
        pass

    @cli.command('hello', short_help='打個招呼')
    @click.argument('name')
    def hello(name):
        print(f'哈囉 {name}')

    @cli.command('serve', short_help='啟動理財機器人')
    @click.option('--host', default='0.0.0.0', help='啟動的 host')
    @click.option('-p', '--port', default=8888, help='啟動的 port')
    @click.option('-d', '--dev', is_flag=True, default=False, help='開發者模式')
    def serve(host: str, port: int, dev: bool):
        print(f'啟動理財機器人 {host}:{port} (dev: {dev}) ...')
        server = APIServer()
        server.serve(
            host=host,
            port=port,
            is_dev=dev,
        )

    @cli.group('remote')
    def remote():
        pass

    @remote.command('ping')
    @click.option('--url', default='http://localhost:8888', help='理財機器人的 URL')
    def ping(url):
        try:
            resp = requests.get(f'{url}/debug/ping')
            print(resp.text)
        except requests.exceptions.RequestException:
            print(f'理財機器人 ({url}) 連線失敗')

    return cli
