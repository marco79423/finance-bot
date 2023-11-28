import click

from finance_bot.core.schedule import Schedule


def create_schedule_cli():
    @click.group('schedule')
    def schedule():
        """排程"""
        pass

    s = Schedule()

    @schedule.command("start")
    def start():
        """啟動服務"""
        s.start()

    return schedule
