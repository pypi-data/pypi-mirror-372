import datetime
import functools

from .impl import hapi


@functools.total_ordering
class Date:
    """
    A Hyper DATE value - year, month, and day.

    This class is similar to ``datetime.date``. The difference is that it supports a greater range of dates: while
    Python years range from 1 to 9999, Hyper supports years from ``-4712`` (4713 BC) to ``294276``.

    :param year: the year.
    :param month: the month, from 1 to 12.
    :param day: the day, from 1 to the number of days in the month.

    .. testsetup:: Date.__init__

        from tableauhyperapi import *

    .. doctest:: Date.__init__

        >>> print(Date(2019, 6, 13))
        2019-06-13

    """

    MINYEAR = -4712
    """ The earliest representable year. """

    MAXYEAR = 294276
    """ The latest representable year. """

    __slots__ = ('year', 'month', 'day')

    def __init__(self, year, month, day):
        self.year = year
        """ The year."""
        self.month = month
        """ The month."""
        self.day = day
        """ The day."""

    @staticmethod
    def today() -> 'Date':
        """ Returns the current local date. """
        return Date.from_date(datetime.date.today())

    @staticmethod
    def from_date(date: datetime.date) -> 'Date':
        """ Converts Python ``datetime.date`` to :any:`Date`. """
        return Date(date.year, date.month, date.day)

    def to_date(self) -> datetime.date:
        """
        Converts to Python ``datetime.date``. Raises an exception if the date is not representable by the
        Python class.
        """
        return datetime.date(self.year, self.month, self.day)

    @staticmethod
    def _from_hyper(v):
        comps = hapi.hyper_decode_date(v)
        return Date(comps.year, comps.month, comps.day)

    def __repr__(self):
        return f'Date({self.year}, {self.month}, {self.day})'

    def __str__(self):
        return f'{self.year}-{self.month:02}-{self.day:02}'

    def __eq__(self, other):
        if not isinstance(other, Date):
            return NotImplemented
        return self.year == other.year and self.month == other.month and self.day == other.day

    def __lt__(self, other):
        if not isinstance(other, Date):
            return NotImplemented
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)

    def __hash__(self):
        return hash((self.year, self.month, self.day))
