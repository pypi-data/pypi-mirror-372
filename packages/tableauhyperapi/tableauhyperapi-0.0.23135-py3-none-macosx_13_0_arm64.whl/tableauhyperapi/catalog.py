from pathlib import PurePath
from typing import Union, Optional, List

from .connection import Connection
from .tablename import Name, SchemaName, TableName, DatabaseName
from .tabledefinition import TableDefinition
from .impl import hapi
from .impl.dll import ffi
from .impl.dllutil import Error, InteropUtil, NativeTableDefinition
from .impl.schemaconverter import SchemaConverter


class Catalog:
    """
    The class which is responsible for querying and manipulating metadata.

    Do not create instances of this class, use :any:`Connection.catalog` instead.
    """

    def __init__(self, connection: Connection):
        self.__connection = connection

    @property
    def connection(self) -> Connection:
        """ Gets the underlying connection. """
        return self.__connection

    @property
    def __cdata(self):
        return self.__connection._cdata

    def has_table(self, name: Union[TableName, Name, str]) -> bool:
        """ Does a table with this name exist? """
        p_exists = ffi.new('bool*')
        database_name, schema_name, table_name = TableName(name)._unescaped_triple
        Error.check(hapi.hyper_has_table(self.__cdata,
                                         InteropUtil.string_to_char_p(database_name),
                                         InteropUtil.string_to_char_p(schema_name),
                                         InteropUtil.string_to_char_p(table_name),
                                         p_exists))
        return p_exists[0] != 0

    def get_table_definition(self, name: Union[TableName, Name, str]) -> TableDefinition:
        """ Gets a table definition. Raises an exception if the table does not exist. """
        database_name, schema_name, table_name = TableName(name)._unescaped_triple
        pp_table_def = ffi.new('hyper_table_definition_t**')
        Error.check(hapi.hyper_get_table_definition(self.__cdata,
                                                    InteropUtil.string_to_char_p(database_name),
                                                    InteropUtil.string_to_char_p(schema_name),
                                                    InteropUtil.string_to_char_p(table_name),
                                                    pp_table_def))
        native = NativeTableDefinition(pp_table_def[0])
        return SchemaConverter.table_definition_from_native(native)

    def __create_table(self, table_definition: TableDefinition, fail_if_exists: bool):
        native_table_def = SchemaConverter.table_definition_to_native(table_definition)
        Error.check(hapi.hyper_create_table(self.__cdata, native_table_def.cdata, fail_if_exists))

    def create_table(self, table_definition: TableDefinition):
        """
        Creates a table. Raise an exception if the table already exists.

        :param table_definition: the table definition.
        """
        self.__create_table(table_definition, True)

    def create_table_if_not_exists(self, table_definition: TableDefinition):
        """
        Creates a table if it does not already exist, otherwise does nothing.

        :param table_definition: the table definition.
        """
        self.__create_table(table_definition, False)

    def get_schema_names(self, database: Union[DatabaseName, Name, str] = None) -> List[SchemaName]:
        """
        Gets the names of all schemas of the database specified by the database name, or of the first database in
        the search path if the name is not specified.
        """
        database_name = DatabaseName(database)._unescaped if database else None
        pp_names = ffi.new('hyper_string_list_t**')
        Error.check(hapi.hyper_get_schema_names(self.__cdata,
                                                InteropUtil.string_to_char_p(database_name),
                                                pp_names))
        return [SchemaName(database, name) for name in InteropUtil.convert_and_free_string_list(pp_names)]

    def get_table_names(self, schema: Union[SchemaName, Name, str]) -> List[TableName]:
        """ Gets the names of all tables in the specified schema. """
        database_name, schema_name = SchemaName(schema)._unescaped_double
        pp_names = ffi.new('hyper_string_list_t**')
        Error.check(hapi.hyper_get_table_names(self.__cdata,
                                               InteropUtil.string_to_char_p(database_name),
                                               InteropUtil.string_to_char_p(schema_name),
                                               pp_names))
        return [TableName(schema, name) for name in InteropUtil.convert_and_free_string_list(pp_names)]

    def __create_schema(self, schema: Union[str, Name, SchemaName], fail_if_exists: bool):
        schema = SchemaName(schema)
        db_name, schema_name = schema._unescaped_double
        Error.check(hapi.hyper_create_schema(self.__cdata,
                                             InteropUtil.string_to_char_p(db_name),
                                             InteropUtil.string_to_char_p(schema_name),
                                             fail_if_exists))

    def create_schema(self, schema: Union[str, Name, SchemaName]):
        """
        Creates a new schema with the given name. The schema must not already exist.

        :param schema: the name of the schema.
        """
        self.__create_schema(schema, True)

    def create_schema_if_not_exists(self, schema: Union[str, Name, SchemaName]):
        """
        Creates a new schema with the given name if it does not already exist, otherwise does nothing.

        :param schema: the name of the schema.
        """
        self.__create_schema(schema, False)

    def create_database(self, database_path: Union[str, PurePath]):
        """
        Creates a new database at the given path. The file must not already exist. It does not attach the database
        to the current connection.

        :param database_path: path to the database file.
        """
        Error.check(hapi.hyper_create_database(self.__cdata,
                                               InteropUtil.string_to_char_p(str(database_path)),
                                               True))

    def create_database_if_not_exists(self, database_path: Union[str, PurePath]):
        """
        Creates a new database at the given path if it does not already exist, otherwise does nothing. It does not
        attach the database to the current connection.

        Note: This method raises an exception if a file that is not a hyper database exists at the given path.

        :param database_path: path to the database file.
        """
        Error.check(hapi.hyper_create_database(self.__cdata,
                                               InteropUtil.string_to_char_p(str(database_path)),
                                               False))

    def attach_database(self, database_path: Union[str, PurePath],
                        alias: Optional[Union[str, Name, DatabaseName]] = None):
        """ Attaches a database to the underlying connection. """
        db_path = database_path if isinstance(database_path, PurePath) else PurePath(database_path)

        if not alias:
            alias = db_path.stem
        alias = DatabaseName(alias)

        Error.check(hapi.hyper_attach_database(self.__cdata,
                                               InteropUtil.string_to_char_p(str(db_path)),
                                               InteropUtil.string_to_char_p(alias._unescaped)))

    def detach_database(self, alias: Union[str, Name, DatabaseName]):
        """ Detaches a database from the underlying connection. """
        alias = DatabaseName(alias)
        Error.check(hapi.hyper_detach_database(self.__cdata, InteropUtil.string_to_char_p(alias._unescaped)))

    def detach_all_databases(self):
        """ Detaches all databases from the underlying connection. """
        Error.check(hapi.hyper_detach_all_databases(self.__cdata))

    def drop_database(self, database_path: Union[str, PurePath]):
        """ Drops a database file. Raise an exception if the database does not exist. """
        Error.check(hapi.hyper_drop_database(self.__cdata, InteropUtil.string_to_char_p(str(database_path)), True))

    def drop_database_if_exists(self, database_path: Union[str, PurePath]):
        """ Drops a database file if it exists, otherwise does nothing. """
        Error.check(hapi.hyper_drop_database(self.__cdata, InteropUtil.string_to_char_p(str(database_path)), False))
