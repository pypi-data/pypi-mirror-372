import functools
from typing import Optional

from .name import _parse_name_arguments
from .schemaname import SchemaName, DatabaseName, Name
from .impl.util import less_than_for_pairs_first_optional


@functools.total_ordering
class TableName:
    """
    An escaped and potentially qualified TableName.

    :param components: the unescaped components of the table name.

    Examples:

    .. testsetup:: TableName

        from tableauhyperapi import *

    .. doctest:: TableName

        >>> print(TableName('table'))
        "table"
        >>> print(TableName('schema', 'table'))
        "schema"."table"
        >>> print(TableName('db', 'schema', 'table'))
        "db"."schema"."table"
        >>> print('CREATE TABLE {}'.format(TableName('db', 'schema', 'table')))
        CREATE TABLE "db"."schema"."table"
        >>> print('CREATE TABLE {}'.format(TableName('schema','table')))
        CREATE TABLE "schema"."table"
    """

    def __init__(self, *components):

        parsed_comps, parsed_comps_type_known = _parse_name_arguments(*components)
        if parsed_comps_type_known:
            db_name, schema_name, table_name = parsed_comps
            if not table_name:
                raise ValueError('Table name is missing')
        elif len(parsed_comps) > 3:
            raise ValueError('Too many components in the table name')
        elif len(parsed_comps) == 3:
            db_name, schema_name, table_name = parsed_comps
        elif len(parsed_comps) == 2:
            db_name, schema_name, table_name = None, parsed_comps[0], parsed_comps[1]
        else:
            db_name, schema_name, table_name = None, None, parsed_comps[0]

        assert isinstance(table_name, str)
        assert not db_name or schema_name

        self.__table_name = Name(table_name)
        self.__schema_name = SchemaName(db_name, schema_name) if schema_name else None

        if self.__schema_name:
            self.__escaped_name = str(self.__schema_name) + '.' + str(self.__table_name)
        else:
            self.__escaped_name = str(self.__table_name)

    @property
    def name(self) -> Name:
        """
        The table name, i.e., the last part of a fully qualified table name.
        """
        return self.__table_name

    @property
    def schema_name(self) -> Optional[SchemaName]:
        """
        The schema name or None
        """
        return self.__schema_name

    @property
    def database_name(self) -> Optional[DatabaseName]:
        """
        The database name or None
        """
        return self.__schema_name.database_name if self.__schema_name else None

    @property
    def _unescaped_components(self):
        if self.__schema_name:
            return self.__schema_name._unescaped_components + [self.__table_name.unescaped]
        else:
            return [self.__table_name.unescaped]

    @property
    def _unescaped_triple(self):
        if self.__schema_name:
            database_name, schema_name = self.__schema_name._unescaped_double
            return database_name, schema_name, self.__table_name.unescaped
        else:
            return None, None, self.__table_name.unescaped

    @property
    def is_fully_qualified(self) -> bool:
        """
        Is the table name fully qualified, i.e., it contains a schema name and a database name
        """
        return self.__schema_name is not None and self.__schema_name.is_fully_qualified

    def __str__(self):
        return self.__escaped_name

    def __repr__(self):
        return 'TableName({})'.format(', '.join(map(repr, self._unescaped_components)))

    def __hash__(self):
        return hash((self.__schema_name, self.__table_name))

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, TableName):
            return self.__escaped_name == other.__escaped_name

        return NotImplemented

    def __lt__(self, other):
        if not isinstance(other, TableName):
            return NotImplemented

        return less_than_for_pairs_first_optional((self.__schema_name, self.__table_name),
                                                  (other.__schema_name, other.__table_name))
