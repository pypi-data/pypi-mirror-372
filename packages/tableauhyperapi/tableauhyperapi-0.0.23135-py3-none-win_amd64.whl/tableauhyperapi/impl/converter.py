import datetime

from typing import Union

from . import hapi
from .util import MICROSECONDS_PER_DAY
from .. import timestamp  # noqa F401


class Converter:
    """ Convert between date/time objects and integer values used by Hyper. """

    @staticmethod
    def time_to_hyper(v: Union[datetime.time, datetime.datetime]):
        return hapi.hyper_encode_time([v.hour, v.minute, v.second, v.microsecond])

    @staticmethod
    def to_hyper_timestamp(v: Union[datetime.datetime, 'timestamp.Timestamp']):
        try:
            return v._hyper_value
        except AttributeError:
            pass
        v_date = hapi.hyper_encode_date([v.year, v.month, v.day])
        v_time = hapi.hyper_encode_time([v.hour, v.minute, v.second, v.microsecond])
        return v_time + v_date * MICROSECONDS_PER_DAY

    @staticmethod
    def to_hyper_timestamp_tz(v: Union[datetime.datetime, 'timestamp.Timestamp']):
        if v.tzinfo is not None:
            v = v.astimezone(datetime.timezone.utc)
        return Converter.to_hyper_timestamp(v)

    @staticmethod
    def time_from_hyper(v: int) -> datetime.time:
        comps = hapi.hyper_decode_time(v)
        return datetime.time(comps.hour, comps.minute, comps.second, comps.microsecond)
