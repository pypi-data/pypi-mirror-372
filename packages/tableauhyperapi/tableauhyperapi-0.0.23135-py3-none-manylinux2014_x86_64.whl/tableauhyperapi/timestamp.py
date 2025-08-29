import datetime
import functools

from typing import Tuple

from . import date
from .impl.util import MICROSECONDS_PER_SECOND, MICROSECONDS_PER_DAY, c_modulus, c_divide
from .impl import hapi


@functools.total_ordering
class Timestamp:
    """
    A Hyper timestamp - date and time of day.

    This class is similar to ``datetime.datetime``. The difference is that it supports a greater range of dates: while
    Python years range from 1 to 9999, Hyper supports years from ``-4712`` (4713 BC) to ``294276``.

    :param year: Year.
    :param month: Month, from 1 to 12.
    :param day: Day, from 1 to the number of days in the month.
    :param hour: Optional hour value, from 0 to 23.
    :param minute: Optional minute value, from 0 to 59.
    :param second: Optional second value, from 0 to 59.
    :param microsecond: Optional microsecond value, from 0 to 999_999.
    :param tzinfo: Optional tzinfo value, may be None or an instance of a tzinfo subclass.

    .. testsetup:: Timestamp.__init__

        from tableauhyperapi import *

    .. doctest:: Timestamp.__init__

        >>> print(Timestamp(2019, 6, 13))
        2019-06-13 00:00:00
        >>> print(Timestamp(2019, 6, 13, 13, 23, 45))
        2019-06-13 13:23:45
        >>> print(Timestamp(2019, 6, 13, 13, 23, 45, 789876))
        2019-06-13 13:23:45.789876

    """

    MINYEAR = -4712
    """ The earliest representable year. """

    MAXYEAR = 294276
    """ The latest representable year. """

    def __init__(self, *args, tzinfo=None):
        self.__tzinfo = tzinfo

        if len(args) == 1:
            self._hyper_value = args[0]
            return

        if len(args) == 3:
            vd = hapi.hyper_encode_date(args)
            vt = 0
        elif len(args) == 6:
            vd = hapi.hyper_encode_date(args[:3])
            vt = hapi.hyper_encode_time(args[3:] + (0,))
        elif len(args) == 7:
            vd = hapi.hyper_encode_date(args[:3])
            vt = hapi.hyper_encode_time(args[3:])
        else:
            raise ValueError('Invalid number of arguments, expected 3, 6, or 7')

        self._hyper_value = vd * MICROSECONDS_PER_DAY + vt

    @staticmethod
    def today() -> 'Timestamp':
        """ Returns the current local date. """
        return Timestamp.from_datetime(datetime.datetime.today())

    @staticmethod
    def now(tz=None) -> 'Timestamp':
        """
        Returns the current local date and time. If `tz` is not `None`, it must be an instance of a `tzinfo`
        subclass, and the current date and time are converted to `tz`'s time zone.
        """
        return Timestamp.from_datetime(datetime.datetime.now(tz))

    @staticmethod
    def from_date(value: [datetime.date, 'date.Date']) -> 'Timestamp':
        """ Converts a Python ``datetime.date`` or :any:`Date` value to a :any:`Timestamp`. """
        return Timestamp(value.year, value.month, value.day)

    def date(self) -> 'Timestamp':
        """ Gets the date part of this value. """
        year, month, day = self.__decode_date()
        return Timestamp(year, month, day)

    def to_date(self) -> 'date.Date':
        """ Gets the date part of this value as a :any:`Date`. """
        year, month, day = self.__decode_date()
        return date.Date(year, month, day)

    @staticmethod
    def from_datetime(value: datetime.datetime) -> 'Timestamp':
        """ Converts a Python ``datetime.datetime`` value to a :any:`Timestamp`. """
        return Timestamp(value.year, value.month, value.day, value.hour, value.minute, value.second, value.microsecond,
                         tzinfo=value.tzinfo)

    def to_datetime(self) -> datetime.datetime:
        """ Converts this value to Python ``datetime.datetime``. """
        year, month, day = self.__decode_date()
        hour, minute, second, microsecond = self.__decode_time()
        return datetime.datetime(year, month, day, hour, minute, second, microsecond, self.__tzinfo)

    def __to_datetime_restrict(self) -> datetime.datetime:
        """
        Converts this value to Python ``datetime.datetime``. When the `year` component is outside of the range
        datetime.MINYEAR..datetime.MAXYEAR, it is restricted to this range.
        """
        year, month, day = self.__decode_date()
        hour, minute, second, microsecond = self.__decode_time()
        if year > datetime.MAXYEAR:
            year = datetime.MAXYEAR
        elif year < datetime.MINYEAR:
            year = datetime.MINYEAR
        return datetime.datetime(year, month, day, hour, minute, second, microsecond, tzinfo=self.__tzinfo)

    def __decode_date(self) -> Tuple[int, int, int]:
        comps = hapi.hyper_decode_date(c_divide(self._hyper_value, MICROSECONDS_PER_DAY))
        return comps.year, comps.month, comps.day

    def __decode_time(self) -> Tuple[int, int, int, int]:
        comps = hapi.hyper_decode_time(c_modulus(self._hyper_value, MICROSECONDS_PER_DAY))
        return comps.hour, comps.minute, comps.second, comps.microsecond

    def utcoffset(self) -> datetime.timedelta:
        """
        If tzinfo is None, returns None. Otherwise, returns the timedelta returned by self.tzinfo.utcoffset(datetime).
        `datetime` is obtained by converting the timestamp to a datetime restricting the year to the range
        datetime.MINYEAR..datetime.MAXYEAR. This method raises an exception if self.tzinfo.utcoffset(datetime) doesn’t
        return None or a timedelta object representing a whole number of minutes with magnitude less than one day.
        """
        return self.__to_datetime_restrict().utcoffset()

    def _format_utcoffset(self):
        """ Format the UTC offset in the format '+HH:MM[:SS]' """
        utcoffset = self.utcoffset()
        if utcoffset is not None:
            sign = '-' if utcoffset.days < 0 else '+'
            total = abs(utcoffset.seconds + utcoffset.days * 24 * 60 * 60)
            tz_seconds = total % 60
            total //= 60
            tz_minutes = total % 60
            total //= 60
            tz_hours = total
            if tz_seconds == 0:
                return f'{sign}{tz_hours:02}:{tz_minutes:02}'
            else:
                return f'{sign}{tz_hours:02}:{tz_minutes:02}:{tz_seconds:02}'
        return ''

    @staticmethod
    def __timedelta_to_microseconds(v: datetime.timedelta):
        return v.days * MICROSECONDS_PER_DAY + v.seconds * MICROSECONDS_PER_SECOND + v.microseconds

    def astimezone(self, tz=None):
        """
        Return a Timestamp object with new tzinfo attribute tz, adjusting the date and time data so the result is the
        same UTC time as self, but in tz’s local time.

        If provided, tz must be an instance of a tzinfo subclass, and its utcoffset() and dst() methods must not return
        None. If self is naive, it is presumed to represent time in the system timezone.

        If called without arguments (or with tz=None) the system local timezone is assumed for the target timezone. The
        .tzinfo attribute of the converted timestamp instance will be set to an instance of timezone with the zone name
        and offset obtained from the OS.
        """
        dt = self.__to_datetime_restrict()
        current_tz = self.__tzinfo if self.__tzinfo is not None else dt.astimezone().tzinfo
        new_tz = tz if tz is not None else dt.astimezone().tzinfo
        current_offset = Timestamp.__timedelta_to_microseconds(current_tz.utcoffset(dt))
        new_offset = Timestamp.__timedelta_to_microseconds(new_tz.utcoffset(dt))
        return Timestamp(self._hyper_value - current_offset + new_offset, tzinfo=new_tz)

    @property
    def year(self) -> int:
        """ Gets the year part of this value. """
        year, month, day = self.__decode_date()
        return year

    @property
    def month(self) -> int:
        """ Gets the month part of this value, as a number between 1 and 12. """
        year, month, day = self.__decode_date()
        return month

    @property
    def day(self) -> int:
        """ Gets the day part of this value, as a number between 1 and the number of days in the month. """
        year, month, day = self.__decode_date()
        return day

    @property
    def hour(self) -> int:
        """ Gets the hour part of this value, as a number between 0 and 23. """
        hour, minute, second, microsecond = self.__decode_time()
        return hour

    @property
    def minute(self) -> int:
        """ Gets the minute part of this value, as a number between 0 and 59. """
        hour, minute, second, microsecond = self.__decode_time()
        return minute

    @property
    def second(self) -> int:
        """ Gets the second part of this value, as an integer between 0 and 59. """
        hour, minute, second, microsecond = self.__decode_time()
        return second

    @property
    def microsecond(self) -> int:
        """ Gets the second part of this value, as an integer between 0 and 999999. """
        hour, minute, second, microsecond = self.__decode_time()
        return microsecond

    @property
    def tzinfo(self) -> datetime.tzinfo:
        """ Gets the tzinfo of this value, may be None or an instance of a tzinfo subclass. """
        return self.__tzinfo

    def __repr__(self):
        year, month, day = self.__decode_date()
        hour, minute, second, microsecond = self.__decode_time()
        return f'Timestamp({year}, {month}, {day}, {hour}, {minute}, {second}, {microsecond}, {self.__tzinfo})'

    def __str__(self):
        year, month, day = self.__decode_date()
        hour, minute, second, microsecond = self.__decode_time()
        offset = self._format_utcoffset()
        if microsecond == 0:
            return f'{year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}{offset}'
        else:
            return f'{year}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}.{microsecond:06}{offset}'

    def __eq__(self, other):
        if isinstance(other, Timestamp):
            # both naive or both aware with the same tzinfo
            if self.__tzinfo is other.__tzinfo:
                return self._hyper_value == other._hyper_value
            offset1 = self.utcoffset()
            offset2 = other.utcoffset()
            # both naive
            if offset1 is None and offset2 is None:
                return self._hyper_value == other._hyper_value
            # one naive, one aware
            if offset1 is None or offset2 is None:
                return False
            # both aware with different tzinfo
            v1 = self._hyper_value - Timestamp.__timedelta_to_microseconds(offset1)
            v2 = other._hyper_value - Timestamp.__timedelta_to_microseconds(offset2)
            return v1 == v2

        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Timestamp):
            # both naive or both aware with the same tzinfo
            if self.__tzinfo is other.__tzinfo:
                return self._hyper_value < other._hyper_value
            offset1 = self.utcoffset()
            offset2 = other.utcoffset()
            # both naive
            if offset1 is None and offset2 is None:
                return self._hyper_value < other._hyper_value
            # one naive, one aware
            if offset1 is None or offset2 is None:
                raise TypeError("can't compare offset-naive and offset-aware timestamps")
            # both aware with different tzinfo
            v1 = self._hyper_value - Timestamp.__timedelta_to_microseconds(offset1)
            v2 = other._hyper_value - Timestamp.__timedelta_to_microseconds(offset2)
            return v1 < v2

        return NotImplemented

    def __hash__(self):
        return hash((self._hyper_value, self.__tzinfo))

    def __add__(self, other):
        if isinstance(other, datetime.timedelta):
            return Timestamp(self._hyper_value + Timestamp.__timedelta_to_microseconds(other), tzinfo=self.__tzinfo)

        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, datetime.timedelta):
            return Timestamp(self._hyper_value - Timestamp.__timedelta_to_microseconds(other), tzinfo=self.__tzinfo)
        if isinstance(other, Timestamp):
            # both naive or both aware with the same tzinfo
            if self.__tzinfo is other.__tzinfo:
                return datetime.timedelta(microseconds=self._hyper_value - other._hyper_value)
            offset1 = self.utcoffset()
            offset2 = other.utcoffset()
            # both naive
            if offset1 is None and offset2 is None:
                return datetime.timedelta(microseconds=self._hyper_value - other._hyper_value)
            # one naive, one aware
            if offset1 is None or offset2 is None:
                raise TypeError("can't subtract offset-naive and offset-aware timestamps")
            # both aware with different tzinfo
            v1 = self._hyper_value - Timestamp.__timedelta_to_microseconds(offset1)
            v2 = other._hyper_value - Timestamp.__timedelta_to_microseconds(offset2)
            return datetime.timedelta(microseconds=v1 - v2)

        return NotImplemented
