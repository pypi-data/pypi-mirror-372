import functools
from pathlib import PurePath
from typing import Union, Tuple, List, Any

from .impl import hapi
from .impl.dllutil import invoke_native_string_transform_function


@functools.total_ordering
class Name:
    """
    An object which represents a SQL object name.
    It handles quoting and escaping strings to avoid SQL injection attacks.

    :param name: the raw, unquoted, unescaped name.

    Example:

    .. testsetup:: Name

        from tableauhyperapi import *

    .. doctest:: Name

        >>> print(Name('a table'))
        "a table"
        >>> print(f'DROP TABLE {Name("a table")}')
        DROP TABLE "a table"
    """

    def __init__(self, name: Union[str, PurePath, 'Name']):

        if not name:
            raise ValueError('Name may not be empty')

        # Allow escaping escaped names - it is needed so we can safely do something like
        # def foo(name: Union[str, Name]):
        #     escaped_for_sure = Name(name)
        #     ...
        if isinstance(name, Name):
            name = name.unescaped
        else:
            # weird import here because it's a circular dependency otherwise
            from . import databasename, tablename, schemaname
            if isinstance(name, databasename.DatabaseName) or isinstance(name, schemaname.SchemaName) or \
                    isinstance(name, tablename.TableName):
                # But do not allow TableName, SchemaName or DatabaseName here, or we will get stuff like """a"".""b""".
                # We could allow single-component names, but it's better to be more strict.
                raise ValueError(f'Cannot escape a {type(name).__name__} instance')

        name = str(name)
        self.__unescaped_name = name
        self.__escaped_name = invoke_native_string_transform_function(hapi.hyper_quote_sql_identifier, name)

    @property
    def unescaped(self) -> str:
        """
        The unescaped name that was used to create this name. Don't use the result of this method in SQL,
        as it is prone to SQL injection. The method should be used where the original name is required (e.g., logging).
        """
        return self.__unescaped_name

    def __str__(self):
        return self.__escaped_name

    def __repr__(self):
        return 'Name({})'.format(repr(self.__unescaped_name))

    def __hash__(self):
        return hash(self.__escaped_name)

    def __eq__(self, other):
        if other is None:
            return False

        if isinstance(other, Name):
            return str(self) == str(other)

        return NotImplemented

    def __lt__(self, other):
        if not isinstance(other, Name):
            return NotImplemented

        return self.__unescaped_name < other.__unescaped_name


def _parse_name_arguments2(*args) -> Tuple[List[str], bool]:
    """
    Helper for _parse_name_arguments(). Args passed here are all single-component name objects, like
    SchemaName('schema') or Name('x').
    """

    from .tablename import DatabaseName, SchemaName, TableName

    db_name, schema_name, table_name = None, None, None
    anonymous_comps = []

    for arg in args:
        if isinstance(arg, DatabaseName):
            if db_name:
                raise ValueError('Database name is specified twice')
            if anonymous_comps or schema_name or table_name:
                raise ValueError('Database name is specified after other components')
            db_name = arg._unescaped
        elif isinstance(arg, SchemaName):
            assert not arg.database_name
            if schema_name:
                raise ValueError('Schema name is specified twice')
            if table_name:
                raise ValueError('Schema name is specified after table name')
            elif len(anonymous_comps) > 1:
                raise ValueError('Schema name is specified twice')
            elif len(anonymous_comps) == 1:
                db_name = anonymous_comps[0]
                anonymous_comps = []
            schema_name = arg.name.unescaped
        elif isinstance(arg, TableName):
            assert not arg.schema_name
            if table_name or len(anonymous_comps) > 2:
                raise ValueError('Table name is specified twice')
            elif anonymous_comps:
                if len(anonymous_comps) == 2:
                    db_name, schema_name = anonymous_comps
                else:
                    schema_name = anonymous_comps[0]
                anonymous_comps = []
            elif db_name and not schema_name:
                raise ValueError('Schema name is missing')
            table_name = arg.name.unescaped
        elif arg:
            if isinstance(arg, Name):
                arg = arg.unescaped
            else:
                arg = str(arg)
            if table_name:
                raise ValueError('Table name is specified twice')
            elif schema_name:
                table_name = arg
            elif db_name:
                schema_name = arg
            elif len(anonymous_comps) >= 3:
                raise ValueError('Too many components in the name')
            else:
                anonymous_comps.append(arg)
        # trailing None is allowed and ignored
        elif anonymous_comps or db_name or schema_name or table_name:
            raise ValueError('Name component may not be None or empty')

    if db_name or schema_name or table_name:
        return [db_name, schema_name, table_name], True
    elif not anonymous_comps:
        raise ValueError('Name may not be empty')
    else:
        return anonymous_comps, False


def _unpack_arg(arg: Any, unpacked_args: List[Any]):
    from .tablename import SchemaName, TableName
    if isinstance(arg, SchemaName) and arg.database_name:
        unpacked_args.append(arg.database_name)
        unpacked_args.append(SchemaName(arg.name))
    elif isinstance(arg, TableName) and arg.schema_name:
        _unpack_arg(arg.schema_name, unpacked_args)
        unpacked_args.append(TableName(arg.name))
    else:
        unpacked_args.append(arg)


def _parse_name_arguments(*args) -> Tuple[List[str], bool]:
    """
    Parse a sequence of arguments into db, schema, table name triple, if the parameters are such that we
    can determine what's what; second return value is True in this case. If it's just a sequence of strings or Names,
    then it returns that, and the second return value is False.

    It raises exceptions if it encounters something weird, like TableName followed by anything, or DatabaseName
    followed by a TableName without a schema name.

    This is a helper method for DatabaseName, SchemaName, TableName constructors. Example:
        ('a') -> ('a'), False -- can't determine whether it's a database, schema, or table name
        ('a', 'b') -> ('a', 'b'), False -- same here
        (DatabaseName('a')) -> ('a', None, None), True --  we do know it's a database name
        (DatabaseName('a'), SchemaName('b')) -> ('a', 'b', None), True -- we do know it's database and schema names
        (SchemaName('b')) -> (None, 'b', None), True -- we do know it's a schema name
    """
    transformed_args = []
    for arg in args:
        _unpack_arg(arg, transformed_args)
    return _parse_name_arguments2(*transformed_args)
