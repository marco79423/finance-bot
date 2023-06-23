import click

from finance_bot.server.api_server import APIServer


def create_server_cli():
    @click.command('serve', short_help='啟動理財機器人')
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

    return serve
