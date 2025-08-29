import functools
from typing import Optional, Tuple, List

from .databasename import DatabaseName, Name
from .name import _parse_name_arguments
from .impl.util import less_than_for_pairs_first_optional


@functools.total_ordering
class SchemaName:
    """
    An escaped and potentially qualified Schema Name.

    :param components: the unescaped components of the schema name.

    Examples:

    .. testsetup:: SchemaName

        from tableauhyperapi import *

    .. doctest:: SchemaName

        >>> print(SchemaName('schema'))
        "schema"
        >>> print(SchemaName('database', 'schema'))
        "database"."schema"
        >>> print('CREATE SCHEMA {}'.format(SchemaName('db', 'a schema')))
        CREATE SCHEMA "db"."a schema"
    """

    def __init__(self, *components):

        parsed_comps, parsed_comps_type_known = _parse_name_arguments(*components)
        if parsed_comps_type_known:
            db_name, schema_name, table_name = parsed_comps
            if table_name:
                raise ValueError('Table name may not be specified in schema name')
            if not schema_name:
                raise ValueError('Schema name is missing')
        elif len(parsed_comps) > 2:
            raise ValueError('Too many components in the schema name')
        elif len(parsed_comps) == 2:
            db_name, schema_name = parsed_comps
        else:
            db_name, schema_name = None, parsed_comps[0]

        assert isinstance(schema_name, str)

        self.__schema_name = Name(schema_name)
        self.__database_name = DatabaseName(db_name) if db_name else None

        if self.__database_name:
            self.__escaped_name = str(self.__database_name) + '.' + str(self.__schema_name)
        else:
            self.__escaped_name = str(self.__schema_name)

    @property
    def name(self) -> Name:
        """
        The schema name, i.e., the last part of a fully qualified schema name.
        """
        return self.__schema_name

    @property
    def database_name(self) -> Optional[DatabaseName]:
        """
        The database name or None
        """
        return self.__database_name

    @property
    def _unescaped_components(self) -> List[str]:
        if self.__database_name:
            return [self.__database_name._unescaped, self.__schema_name.unescaped]
        else:
            return [self.__schema_name.unescaped]

    @property
    def _unescaped_double(self) -> Tuple[Optional[str], str]:
        if self.__database_name:
            return self.__database_name._unescaped, self.__schema_name.unescaped
        else:
            return None, self.__schema_name.unescaped

    @property
    def is_fully_qualified(self) -> bool:
        """
        Is the schema name fully qualified, i.e., It contains a database name
        """
        return self.__database_name is not None

    def __str__(self):
        return self.__escaped_name

    def __repr__(self):
        return 'SchemaName({})'.format(', '.join(map(repr, self._unescaped_components)))

    def __hash__(self):
        return hash((self.__database_name, self.__schema_name))

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, SchemaName):
            return self.__escaped_name == other.__escaped_name

        return NotImplemented

    def __lt__(self, other):
        if not isinstance(other, SchemaName):
            return NotImplemented

        return less_than_for_pairs_first_optional((self.__database_name, self.__schema_name),
                                                  (other.__database_name, other.__schema_name))
