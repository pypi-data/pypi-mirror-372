import functools

from typing import Union

from .impl.util import c_modulus, c_divide


# TODO TFSID 922857: check limits
@functools.total_ordering
class Interval:
    """
    A Hyper INTERVAL. It is a union of logically independent months, days, and microseconds components, which
    expresses time intervals like "1 year" (which may mean 365 or 366 days depending on to which date it is
    added), "2 months" (which has variable number of days depending on the month), "3 days" (which may mean
    different number of hours if daylight savings changed), "4 hours", "5 seconds".

    :param months: the number of months.
    :param days: the number of days.
    :param microseconds: the number of microseconds.

    Examples:

    .. testsetup:: Interval.__init__

        from tableauhyperapi import *

    .. doctest:: Interval.__init__

        >>> print(Interval(1, 0, 0)) # 1 month
        P1M
        >>> print(Interval(0, 1, 0)) # 1 day
        P1D
        >>> print(Interval(0, 0, 1_000_000)) # 1 second
        PT1.0S

    :any:`Interval` values can be added and subtracted, which performs component-wise addition or subtraction.

    Comparison for :any:`Interval` values is lexicographic on their components, for instance 1 day does not equal 24
    hours. Similarly 1 year compares greater than 400 days.
    """

    __slots__ = ('months', 'days', 'microseconds')

    _MICROSECONDS_PER_HOUR = 60 * 60 * 1_000_000
    _MICROSECONDS_PER_MINUTE = 60 * 1_000_000
    _MICROSECONDS_PER_SECOND = 1_000_000

    def __init__(self, months: int, days: int, microseconds: int):
        self.months = months
        """ The months component. """
        self.days = days
        """ The days component. """
        self.microseconds = microseconds
        """ The microseconds component. """

    @staticmethod
    def _zero() -> 'Interval':
        """ Zero-length interval. """
        return Interval(0, 0, 0)

    @staticmethod
    def _from_years_and_months(years: int, months: int) -> 'Interval':
        """
        Returns an interval for the given number of years and months (which equals 12*years + months).

        :param years: the number of years.
        :param months: the number of months.
        :return: a new :any:`Interval` object.
        """
        return Interval(years * 12 + months, 0, 0)

    @staticmethod
    def _from_days(days: int) -> 'Interval':
        """
        Returns an interval for the given number of days.

        :param days: the number of days.
        :return: a new :any:`Interval` object.
        """
        return Interval(0, days, 0)

    @staticmethod
    def _from_seconds(seconds: Union[int, float]) -> 'Interval':
        """
        Returns an interval for the given number of seconds.

        :param seconds: the number of seconds, may be a floating-point number with microsecond precision.
        :return: a new :any:`Interval` object.
        """
        mus = seconds * Interval._MICROSECONDS_PER_SECOND
        return Interval(0, 0, int(mus))

    @staticmethod
    def _from_time_parts(hours: int = 0, minutes: int = 0, seconds: int = 0, microseconds: int = 0) -> 'Interval':
        """
        Returns an interval for the given number of hours, minutes, seconds, and microseconds.

        :param hours: the number of hours.
        :param minutes: the number of minutes.
        :param seconds: the number of seconds.
        :param microseconds: the number of microseconds.
        :return: a new :any:`Interval` object.
        """
        mus = hours * Interval._MICROSECONDS_PER_HOUR + minutes * Interval._MICROSECONDS_PER_MINUTE + \
            seconds * Interval._MICROSECONDS_PER_SECOND + microseconds
        return Interval(0, 0, mus)

    @property
    def _year_part(self) -> int:
        """ The year part of the (years, months, days, hours, minutes, seconds, microseconds) representation. """
        return c_divide(self.months, 12)

    @property
    def _month_part(self) -> int:
        """ The month part of the (years, months, days, hours, minutes, seconds, microseconds) representation. """
        return c_modulus(self.months, 12)

    @property
    def _day_part(self) -> int:
        """ The day part of the (years, months, days, hours, minutes, seconds, microseconds) representation. """
        return self.days

    @property
    def _hour_part(self) -> int:
        """ The hour part of the (years, months, days, hours, minutes, seconds, microseconds) representation. """
        return c_divide(self.microseconds, Interval._MICROSECONDS_PER_HOUR)

    @property
    def _minute_part(self) -> int:
        """ The minute part of the (years, months, days, hours, minutes, seconds, microseconds) representation. """
        return c_modulus(c_divide(self.microseconds, Interval._MICROSECONDS_PER_MINUTE), 60)

    @property
    def _second_part(self) -> int:
        """ The second part of the (years, months, days, hours, minutes, seconds, microseconds) representation. """
        return c_modulus(c_divide(self.microseconds, Interval._MICROSECONDS_PER_SECOND), 60)

    @property
    def _microsecond_part(self) -> int:
        """ The microsecond part of the (years, months, days, hours, minutes, seconds, microseconds) representation. """
        return c_modulus(self.microseconds, Interval._MICROSECONDS_PER_SECOND)

    def __repr__(self):
        return 'Interval({}, {}, {})'.format(self.months, self.days, self.microseconds)

    def __str__(self):
        """ ISO 8601 timestamp representation (https://en.wikipedia.org/wiki/ISO_8601#Durations) """

        result = 'P'

        if self.months:
            year_part = self._year_part
            if year_part:
                result += '{0}Y'.format(year_part)
            month_part = self._month_part
            if month_part:
                result += '{0}M'.format(month_part)

        if self.days:
            result += '{0}D'.format(self.days)

        if self.microseconds:
            result += 'T'
            hour_part = self._hour_part
            minute_part = self._minute_part
            second_part = self._second_part
            microsecond_part = self._microsecond_part
            if hour_part:
                result += '{0}H'.format(hour_part)
            if minute_part:
                result += '{0}M'.format(minute_part)
            if second_part or microsecond_part:
                result += '{0}S'.format(second_part + microsecond_part / Interval._MICROSECONDS_PER_SECOND)
        elif len(result) == 1:
            result += 'T0S'

        return result

    def __as_tuple(self):
        return self.months, self.days, self.microseconds

    def __eq__(self, other):
        if not isinstance(other, Interval):
            return NotImplemented
        return self.__as_tuple() == other.__as_tuple()

    def __lt__(self, other):
        if not isinstance(other, Interval):
            return NotImplemented
        return self.__as_tuple() < other.__as_tuple()

    def __hash__(self):
        return hash(self.__as_tuple())

    def __bool__(self):
        return bool(self.months or self.days or self.microseconds)

    def __add__(self, other):
        if not isinstance(other, Interval):
            return NotImplemented
        return Interval(self.months + other.months, self.days + other.days, self.microseconds + other.microseconds)

    def __sub__(self, other):
        if not isinstance(other, Interval):
            return NotImplemented
        return Interval(self.months - other.months, self.days - other.days, self.microseconds - other.microseconds)

    def __neg__(self):
        return Interval(-self.months, -self.days, -self.microseconds)

    def __pos__(self):
        return Interval(self.months, self.days, self.microseconds)

    def __abs__(self):
        return Interval(abs(self.months), abs(self.days), abs(self.microseconds))

    def __mul__(self, other):
        if not isinstance(other, int):
            return NotImplemented
        return Interval(self.months * other, self.days * other, self.microseconds * other)
