import click
import requests


def create_remote_cli():
    @click.group('remote')
    def remote():
        """與理財機器人互動"""
        pass

    @remote.command('ping')
    @click.option('--url', default='http://localhost:8888', help='理財機器人的 URL')
    def ping(url):
        try:
            resp = requests.get(f'{url}/debug/ping')
            print(resp.text)
        except requests.exceptions.RequestException:
            print(f'理財機器人 ({url}) 連線失敗')

    return remote
