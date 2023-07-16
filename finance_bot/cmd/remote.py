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

    @remote.group('lending')
    def lending():
        """放貸"""
        pass

    @lending.command('records')
    @click.option('--url', default='http://localhost:8888', help='理財機器人的 URL')
    def ping(url):
        try:
            resp = requests.get(f'{url}/lending/records')
            records = resp.json()
            for record in sorted(records, key=lambda r: r['end']):
                print('金額：{amount:.2f}\t利率：{current_rate:.6f}%\t到期 {end}\t剩下 {last_time}'.format(**record))
        except requests.exceptions.RequestException:
            print(f'理財機器人 ({url}) 連線失敗')

    return remote
