import asyncio

import click

from finance_bot.core.schedule import Schedule


def create_schedule_cli():
    @click.group('schedule')
    def schedule():
        """排程"""
        pass

    s = Schedule()

    @schedule.command("start")
    def start_server():
        """啟動服務"""
        s.start()

    @schedule.command("send")
    @click.argument('task_key')
    def send_task(task_key):
        asyncio.run(s.send_task(task_key))

    return schedule
