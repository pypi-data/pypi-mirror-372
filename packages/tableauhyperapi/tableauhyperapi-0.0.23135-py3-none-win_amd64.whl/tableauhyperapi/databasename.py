import functools
from pathlib import PurePath
from typing import Union

from .name import Name, _parse_name_arguments


@functools.total_ordering
class DatabaseName:
    """
    An escaped Database Name

    :param database_name: the raw, unquoted, unescaped name.

    Example:

    .. testsetup:: DatabaseName

        from tableauhyperapi import *

    .. doctest:: DatabaseName

        >>> print(DatabaseName('database'))
        "database"
        >>> print(f'CREATE DATABASE {DatabaseName("a database")}')
        CREATE DATABASE "a database"
    """

    def __init__(self, database_name: Union[str, PurePath, 'Name', 'DatabaseName']):

        # this seems like overkill, do all this stuff for a single name, but the side
        # effect is that it checks the types, so it will correctly fail for something
        # like DatabaseName(SchemaName('x', 'y')). (If we ever decide that this should
        # produce DatabaseName('x'), then we can do that here too).
        parsed_comps, parsed_comps_type_known = _parse_name_arguments(database_name)
        if parsed_comps_type_known:
            db_name, schema_name, table_name = parsed_comps
            if table_name:
                raise ValueError('Table name is specified instead of database name')
            if schema_name:
                raise ValueError('Schema name is specified instead od database name')
        else:
            assert len(parsed_comps) == 1
            db_name = parsed_comps[0]

        self.__name = Name(db_name)

    @property
    def name(self) -> Name:
        """
        The escaped and quoted database name
        """
        return self.__name

    @property
    def _unescaped(self) -> str:
        """
        The unescaped name that was used to create this name. Don't use the result of this method in SQL,
        as it is prone to SQL injection. The method should be used where the original name is required (e.g. logging).
        """
        return self.__name.unescaped

    def __str__(self):
        return str(self.__name)

    def __repr__(self):
        return 'DatabaseName({})'.format(repr(self._unescaped))

    def __hash__(self):
        return hash(self.__name)

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, DatabaseName):
            return self.__name == other.__name

        return NotImplemented

    def __lt__(self, other):
        if not isinstance(other, DatabaseName):
            return NotImplemented

        return self.__name < other.__name
