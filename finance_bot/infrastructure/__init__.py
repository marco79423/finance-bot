import datetime as dt

import pytz
from dateutil.tz import tzutc

from finance_bot.config import conf


def get_now():
    return dt.datetime.now(tz=pytz.timezone(conf.server.timezone))


def to_server_timezone(time: dt.datetime):
    return time.astimezone(pytz.timezone(conf.server.timezone))


def from_milli_timestamp(millis):
    utc_time = dt.datetime(1970, 1, 1, tzinfo=tzutc()) + dt.timedelta(milliseconds=millis)
    return to_server_timezone(utc_time)
