import click

from finance_bot.cmd.remote import create_remote_cli
from finance_bot.cmd.server import create_server_cli


def create_cli():
    @click.group()
    def cli():
        """兩大類專用理財小工具"""
        pass

    cli.add_command(create_server_cli())
    cli.add_command(create_remote_cli())

    return cli
