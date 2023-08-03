import datetime as dt

import pytz
from dateutil.tz import tzutc

from finance_bot.infrastructure.base import ManagerBase


class TimeManager(ManagerBase):

    def get_now(self):
        return dt.datetime.now(tz=pytz.timezone(self.conf.server.timezone))

    def to_server_timezone(self, time: dt.datetime):
        return time.astimezone(pytz.timezone(self.conf.server.timezone))

    def from_milli_timestamp(self, millis):
        utc_time = dt.datetime(1970, 1, 1, tzinfo=tzutc()) + dt.timedelta(milliseconds=millis)
        return self.to_server_timezone(utc_time)
